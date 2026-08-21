from datetime import datetime, date
from collections import defaultdict
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import (
    db, Faculty, Course, Room, Section, TimeSlot,
    TimetableEntry, LeaveRequest, AcademicCalendarNote, SyllabusProgress
)
from . import teacher_bp
from .auth import role_required

@teacher_bp.before_request
@login_required
@role_required('teacher', 'admin')
def teacher_before_request():
    pass

def get_current_faculty():
    if current_user.role == 'teacher' and current_user.faculty_profile:
        return current_user.faculty_profile
    return Faculty.query.first()

@teacher_bp.route('/')
@teacher_bp.route('/dashboard')
def dashboard():
    faculty = get_current_faculty()
    if not faculty:
        flash("No faculty profile linked to this user.", "warning")
        return redirect(url_for('auth.login'))

    # Active timetable entries for this faculty
    entries = TimetableEntry.query.filter_by(faculty_id=faculty.id, is_active=True).all()
    assigned_count = len(entries)
    
    # Leaves count
    leaves_approved = LeaveRequest.query.filter_by(faculty_id=faculty.id, status='approved').count()
    leaves_pending = LeaveRequest.query.filter_by(faculty_id=faculty.id, status='pending').count()
    my_leaves = LeaveRequest.query.filter_by(faculty_id=faculty.id).order_by(LeaveRequest.created_at.desc()).all()
    
    # Substitution assignments received
    substitutions = LeaveRequest.query.filter_by(substitute_faculty_id=faculty.id, status='approved').all()

    # Syllabus coverage
    progress_records = SyllabusProgress.query.filter_by(faculty_id=faculty.id).all()
    avg_syllabus = round(sum(p.percentage_covered for p in progress_records) / max(len(progress_records), 1)) if progress_records else 0

    # Today's schedule
    today_day = datetime.now().strftime('%A')
    today_slots = [e for e in entries if e.time_slot.day == today_day]
    today_slots.sort(key=lambda x: x.time_slot.period)

    # Days lecture count for chart
    day_counts = defaultdict(int)
    for e in entries:
        day_counts[e.time_slot.day] += 1
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    lectures_per_day = [day_counts[d] for d in days]

    return render_template(
        'teacher/dashboard.html',
        faculty=faculty,
        assigned_count=assigned_count,
        leaves_approved=leaves_approved,
        leaves_pending=leaves_pending,
        my_leaves=my_leaves,
        substitutions=substitutions,
        avg_syllabus=avg_syllabus,
        today_day=today_day,
        today_slots=today_slots,
        days=days,
        lectures_per_day=lectures_per_day
    )

@teacher_bp.route('/timetable')
def timetable():
    faculty = get_current_faculty()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    time_slots = TimeSlot.query.order_by(TimeSlot.period).all()
    
    seen_periods = set()
    periods = []
    for ts in time_slots:
        if ts.period not in seen_periods:
            seen_periods.add(ts.period)
            periods.append(ts)
    periods.sort(key=lambda x: x.period)

    entries = TimetableEntry.query.filter_by(faculty_id=faculty.id, is_active=True).all() if faculty else []
    grid = defaultdict(lambda: defaultdict(list))
    for e in entries:
        grid[e.time_slot.day][e.time_slot.period].append(e)

    return render_template('teacher/timetable.html', faculty=faculty, days=days, periods=periods, grid=grid)

@teacher_bp.route('/apply-leave', methods=['GET', 'POST'])
def apply_leave():
    faculty = get_current_faculty()
    other_faculty = Faculty.query.filter(Faculty.id != faculty.id).all() if faculty else []

    if request.method == 'POST':
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        reason = request.form.get('reason')
        substitute_id = request.form.get('substitute_faculty_id', type=int)

        if start_date_str and end_date_str and reason:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            leave = LeaveRequest(
                faculty_id=faculty.id,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
                substitute_faculty_id=substitute_id if substitute_id else None,
                status='pending'
            )
            db.session.add(leave)
            db.session.commit()
            flash("Leave application submitted successfully! Admin approval pending.", "success")
            return redirect(url_for('teacher.dashboard'))
        else:
            flash("Please fill in all required fields.", "warning")

    my_leaves = LeaveRequest.query.filter_by(faculty_id=faculty.id).order_by(LeaveRequest.created_at.desc()).all() if faculty else []
    return render_template('teacher/apply_leave.html', faculty=faculty, other_faculty=other_faculty, my_leaves=my_leaves)

@teacher_bp.route('/syllabus-progress', methods=['GET', 'POST'])
def syllabus_progress():
    faculty = get_current_faculty()
    
    if request.method == 'POST':
        # Update progress from form
        for key, value in request.form.items():
            if key.startswith('progress_'):
                record_id = int(key.replace('progress_', ''))
                progress_record = SyllabusProgress.query.get(record_id)
                if progress_record and progress_record.faculty_id == faculty.id:
                    progress_record.percentage_covered = int(value)
                    topics_key = f'topics_{record_id}'
                    if topics_key in request.form:
                        progress_record.topics_covered = request.form[topics_key]
        
        db.session.commit()
        flash("Syllabus progress updated successfully!", "success")
        return redirect(url_for('teacher.syllabus_progress'))

    # Find distinct courses assigned to teacher
    assigned_entries = TimetableEntry.query.filter_by(faculty_id=faculty.id, is_active=True).all() if faculty else []
    course_section_pairs = set((e.course_id, e.section_id) for e in assigned_entries)

    # Ensure SyllabusProgress records exist
    progress_records = []
    for c_id, s_id in course_section_pairs:
        rec = SyllabusProgress.query.filter_by(course_id=c_id, faculty_id=faculty.id, section_id=s_id).first()
        if not rec:
            rec = SyllabusProgress(
                course_id=c_id,
                faculty_id=faculty.id,
                section_id=s_id,
                percentage_covered=35,
                topics_covered='Modules 1 & 2 Completed (Foundations & Core Principles)'
            )
            db.session.add(rec)
            db.session.flush()
        progress_records.append(rec)
    
    db.session.commit()

    return render_template('teacher/syllabus_progress.html', faculty=faculty, progress_records=progress_records)

@teacher_bp.route('/academic-calendar')
def academic_calendar():
    faculty = get_current_faculty()
    return render_template('teacher/academic_calendar.html', faculty=faculty)
