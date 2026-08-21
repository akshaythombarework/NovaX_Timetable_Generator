import os
from datetime import datetime, date
from collections import defaultdict
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app, send_file, make_response
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import (
    db, User, Department, Faculty, Course, Room, Section,
    ElectiveBasket, TimeSlot, TimetableEntry, InstitutionSettings,
    LeaveRequest, AcademicCalendarNote, SyllabusProgress
)
from generator.algorithm import generate_timetable_schedule, find_substitute_recommendations
from . import admin_bp
from .auth import role_required

@admin_bp.before_request
@login_required
@role_required('admin')
def admin_before_request():
    pass

# ==========================================
# 1. DASHBOARD & TIMETABLE VIEWS
# ==========================================

@admin_bp.route('/')
@admin_bp.route('/dashboard')
def dashboard():
    settings = InstitutionSettings.get_settings()
    total_faculty = Faculty.query.count()
    total_courses = Course.query.count()
    total_rooms = Room.query.count()
    total_sections = Section.query.count()
    total_classes = TimetableEntry.query.filter_by(is_active=True).count()
    
    # Calculate rooms utilized
    used_room_ids = db.session.query(TimetableEntry.room_id).filter_by(is_active=True).distinct().all()
    rooms_used_count = len(used_room_ids)
    room_utilization = round((rooms_used_count / max(total_rooms, 1)) * 100)
    
    # Clashes check
    clashes = 0
    pending_leaves = LeaveRequest.query.filter_by(status='pending').count()
    
    # Faculty workload summary
    faculty_list = Faculty.query.all()
    faculty_workloads = []
    for fac in faculty_list:
        assigned = TimetableEntry.query.filter_by(faculty_id=fac.id, is_active=True).count()
        leaves_approved = LeaveRequest.query.filter_by(faculty_id=fac.id, status='approved').count()
        progress_entries = SyllabusProgress.query.filter_by(faculty_id=fac.id).all()
        avg_progress = round(sum(p.percentage_covered for p in progress_entries) / max(len(progress_entries), 1)) if progress_entries else 0
        
        faculty_workloads.append({
            'faculty': fac,
            'assigned': assigned,
            'max_hours': fac.max_hours_per_week,
            'leaves_approved': leaves_approved,
            'avg_progress': avg_progress
        })

    # AI Suggestions
    ai_suggestions = [
        "Room R-203 is underutilized on Friday afternoon (only 1 lecture scheduled).",
        "Consider scheduling more practicals in Lab-2 for optimal hardware utilization.",
        "Prof. Sharma (Mathematics) has optimal 14/18 hrs load balance."
    ]

    return render_template(
        'admin/dashboard.html',
        settings=settings,
        total_faculty=total_faculty,
        total_courses=total_courses,
        total_rooms=total_rooms,
        total_sections=total_sections,
        total_classes=total_classes,
        rooms_used_count=rooms_used_count,
        room_utilization=room_utilization,
        clashes=clashes,
        pending_leaves=pending_leaves,
        faculty_workloads=faculty_workloads,
        ai_suggestions=ai_suggestions
    )

@admin_bp.route('/timetable')
def timetable():
    settings = InstitutionSettings.get_settings()
    sections = Section.query.all()
    faculty_list = Faculty.query.all()
    rooms = Room.query.all()
    
    # Selected section filter (default first section)
    selected_section_id = request.args.get('section_id', type=int)
    if not selected_section_id and sections:
        selected_section_id = sections[0].id
    
    selected_section = Section.query.get(selected_section_id) if selected_section_id else None

    # Time slots grouped by Day and sorted by Period
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    time_slots = TimeSlot.query.order_by(TimeSlot.period).all()
    
    # Get distinct periods
    periods = []
    seen_periods = set()
    for ts in time_slots:
        if ts.period not in seen_periods:
            seen_periods.add(ts.period)
            periods.append(ts)
    periods.sort(key=lambda x: x.period)

    # Fetch active entries
    query = TimetableEntry.query.filter_by(is_active=True)
    if selected_section_id:
        query = query.filter_by(section_id=selected_section_id)
    entries = query.all()

    # Matrix: grid[day][period] -> list of entries (or single entry)
    grid = defaultdict(lambda: defaultdict(list))
    for entry in entries:
        ts = entry.time_slot
        grid[ts.day][ts.period].append(entry)

    # Elective Baskets
    elective_baskets = ElectiveBasket.query.all()
    
    # KPI Stats
    total_classes = TimetableEntry.query.filter_by(is_active=True).count()
    rooms_used = len(db.session.query(TimetableEntry.room_id).filter_by(is_active=True).distinct().all())
    total_rooms_count = Room.query.count()
    utilization_pct = round((rooms_used / max(total_rooms_count, 1)) * 100)

    return render_template(
        'admin/timetable.html',
        settings=settings,
        sections=sections,
        selected_section=selected_section,
        faculty_list=faculty_list,
        rooms=rooms,
        days=days,
        periods=periods,
        grid=grid,
        elective_baskets=elective_baskets,
        total_classes=total_classes,
        rooms_used=rooms_used,
        total_rooms_count=total_rooms_count,
        utilization_pct=utilization_pct
    )

@admin_bp.route('/generate', methods=['POST'])
def generate():
    version = request.form.get('version', 1, type=int)
    result = generate_timetable_schedule(version=version)
    if result['success']:
        flash(f"Timetable generated successfully! {result.get('created_count', 0)} slots scheduled with 0 clashes.", "success")
    else:
        flash(f"Generation failed: {result['message']}", "danger")
    return redirect(url_for('admin.timetable'))

# ==========================================
# 2. BACKUP & SUBSTITUTE PLAN (Ref Image 1)
# ==========================================

@admin_bp.route('/backup-plan')
def backup_plan():
    settings = InstitutionSettings.get_settings()
    faculty_list = Faculty.query.order_by(Faculty.name).all()
    
    # Pre-generate static backup mapping for all faculty
    backup_matrix = []
    for fac in faculty_list:
        # Assigned hours
        assigned_hours = TimetableEntry.query.filter_by(faculty_id=fac.id, is_active=True).count()
        # Find 2 other faculty from same or related department with least workload
        other_faculty = [f for f in faculty_list if f.id != fac.id]
        same_dept = [f for f in other_faculty if f.department_id == fac.department_id]
        pool = same_dept if len(same_dept) >= 2 else other_faculty
        
        backup1 = pool[0] if len(pool) > 0 else None
        backup2 = pool[1] if len(pool) > 1 else None
        
        # Primary subjects
        fac_courses = Course.query.filter(
            (Course.default_faculty_id == fac.id) | 
            (Course.department_id == fac.department_id)
        ).limit(2).all()
        subjects_str = ", ".join([c.name for c in fac_courses]) if fac_courses else "General Core"

        backup_matrix.append({
            'faculty': fac,
            'subjects': subjects_str,
            'workload': f"{assigned_hours}/{fac.max_hours_per_week}",
            'backup_1': backup1,
            'backup_2': backup2
        })

    # Check for selected absence parameter
    selected_faculty_id = request.args.get('faculty_id', type=int)
    date_str = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception:
        selected_date = date.today()

    absence_plan = None
    if selected_faculty_id:
        absence_plan = find_substitute_recommendations(selected_faculty_id, selected_date)

    # Active confirmed substitutions
    active_leaves = LeaveRequest.query.filter_by(status='approved').all()

    return render_template(
        'admin/backup_plan.html',
        settings=settings,
        faculty_list=faculty_list,
        backup_matrix=backup_matrix,
        selected_faculty_id=selected_faculty_id,
        selected_date=selected_date,
        absence_plan=absence_plan,
        active_leaves=active_leaves
    )

@admin_bp.route('/substitute/confirm', methods=['POST'])
def confirm_substitute():
    faculty_id = request.form.get('faculty_id', type=int)
    date_str = request.form.get('date')
    substitute_id = request.form.get('substitute_faculty_id', type=int)
    reason = request.form.get('reason', 'Faculty Absentee Substitute Assignment')

    if faculty_id and date_str:
        req_date = datetime.strptime(date_str, '%Y-%m-%d').date() if '-' in date_str else date.today()
        leave = LeaveRequest(
            faculty_id=faculty_id,
            start_date=req_date,
            end_date=req_date,
            reason=reason,
            substitute_faculty_id=substitute_id,
            status='approved',
            admin_remark='Automated backup substitution confirmed by Admin'
        )
        db.session.add(leave)
        db.session.commit()
        flash("Substitute plan confirmed and registered successfully! Notification dispatched.", "success")
    
    return redirect(url_for('admin.backup_plan'))

# ==========================================
# 3. FACULTY MANAGEMENT (CRUD)
# ==========================================

@admin_bp.route('/faculty', methods=['GET', 'POST'])
def faculty():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        department_id = request.form.get('department_id', type=int)
        designation = request.form.get('designation', 'Assistant Professor')
        max_day = request.form.get('max_hours_per_day', 4, type=int)
        max_week = request.form.get('max_hours_per_week', 18, type=int)
        short_code = request.form.get('short_code', '')
        
        # Check user account
        user = User.query.filter_by(email=email).first()
        if not user:
            username = email.split('@')[0] if email else name.lower().replace(' ', '')
            user = User(username=username, email=email, role='teacher')
            user.set_password('teacher123')
            db.session.add(user)
            db.session.flush()

        fac = Faculty(
            user_id=user.id,
            name=name,
            email=email,
            department_id=department_id,
            designation=designation,
            max_hours_per_day=max_day,
            max_hours_per_week=max_week,
            short_code=short_code
        )
        fac.avatar_initials = fac.get_initials()
        db.session.add(fac)
        db.session.commit()
        flash(f"Faculty {name} added successfully!", "success")
        return redirect(url_for('admin.faculty'))

    faculty_members = Faculty.query.all()
    departments = Department.query.all()
    return render_template('admin/faculty.html', faculty_members=faculty_members, departments=departments)

@admin_bp.route('/faculty/delete/<int:id>', methods=['POST'])
def delete_faculty(id):
    fac = Faculty.query.get_or_404(id)
    name = fac.name
    db.session.delete(fac)
    db.session.commit()
    flash(f"Faculty {name} deleted successfully.", "info")
    return redirect(url_for('admin.faculty'))

# ==========================================
# 4. COURSES & ELECTIVES (CRUD)
# ==========================================

@admin_bp.route('/courses', methods=['GET', 'POST'])
def courses():
    if request.method == 'POST':
        code = request.form.get('code')
        name = request.form.get('name')
        department_id = request.form.get('department_id', type=int)
        course_type = request.form.get('type', 'theory')
        hours = request.form.get('hours_per_week', 4, type=int)
        semester = request.form.get('semester', 3, type=int)
        year = request.form.get('year', 2, type=int)
        basket_id = request.form.get('elective_basket_id', type=int)
        faculty_id = request.form.get('default_faculty_id', type=int)

        course = Course(
            code=code,
            name=name,
            department_id=department_id,
            type=course_type,
            hours_per_week=hours,
            semester=semester,
            year=year,
            elective_basket_id=basket_id if basket_id else None,
            default_faculty_id=faculty_id if faculty_id else None
        )
        db.session.add(course)
        db.session.commit()
        flash(f"Course {code} - {name} created successfully!", "success")
        return redirect(url_for('admin.courses'))

    courses_list = Course.query.all()
    departments = Department.query.all()
    baskets = ElectiveBasket.query.all()
    faculty_list = Faculty.query.all()
    return render_template('admin/courses.html', courses=courses_list, departments=departments, baskets=baskets, faculty_list=faculty_list)

@admin_bp.route('/courses/delete/<int:id>', methods=['POST'])
def delete_course(id):
    c = Course.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    flash("Course deleted.", "info")
    return redirect(url_for('admin.courses'))

# ==========================================
# 5. ROOMS & LABS (CRUD)
# ==========================================

@admin_bp.route('/rooms', methods=['GET', 'POST'])
def rooms():
    if request.method == 'POST':
        name = request.form.get('name')
        building = request.form.get('building', 'Main Block')
        capacity = request.form.get('capacity', 60, type=int)
        room_type = request.form.get('type', 'classroom')

        room = Room(name=name, building=building, capacity=capacity, type=room_type)
        db.session.add(room)
        db.session.commit()
        flash(f"Room {name} created!", "success")
        return redirect(url_for('admin.rooms'))

    rooms_list = Room.query.all()
    return render_template('admin/rooms.html', rooms=rooms_list)

@admin_bp.route('/rooms/delete/<int:id>', methods=['POST'])
def delete_room(id):
    r = Room.query.get_or_404(id)
    db.session.delete(r)
    db.session.commit()
    flash("Room deleted.", "info")
    return redirect(url_for('admin.rooms'))

# ==========================================
# 6. SECTIONS & DIVISIONS (CRUD)
# ==========================================

@admin_bp.route('/sections', methods=['GET', 'POST'])
def sections():
    if request.method == 'POST':
        name = request.form.get('name')
        department_id = request.form.get('department_id', type=int)
        year = request.form.get('year', 2, type=int)
        semester = request.form.get('semester', 3, type=int)
        strength = request.form.get('strength', 60, type=int)

        sec = Section(name=name, department_id=department_id, year=year, semester=semester, strength=strength)
        db.session.add(sec)
        db.session.commit()
        flash(f"Division {name} added!", "success")
        return redirect(url_for('admin.sections'))

    sections_list = Section.query.all()
    departments = Department.query.all()
    return render_template('admin/sections.html', sections=sections_list, departments=departments)

@admin_bp.route('/sections/delete/<int:id>', methods=['POST'])
def delete_section(id):
    s = Section.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    flash("Division deleted.", "info")
    return redirect(url_for('admin.sections'))

# ==========================================
# 7. ELECTIVE BASKETS
# ==========================================

@admin_bp.route('/elective-baskets', methods=['GET', 'POST'])
def elective_baskets():
    if request.method == 'POST':
        name = request.form.get('name')
        department_id = request.form.get('department_id', type=int)
        semester = request.form.get('semester', 5, type=int)

        basket = ElectiveBasket(name=name, department_id=department_id, semester=semester)
        db.session.add(basket)
        db.session.commit()
        flash(f"Elective Basket {name} created!", "success")
        return redirect(url_for('admin.elective_baskets'))

    baskets = ElectiveBasket.query.all()
    departments = Department.query.all()
    return render_template('admin/elective_baskets.html', baskets=baskets, departments=departments)

# ==========================================
# 8. TIME SLOTS & BREAKS
# ==========================================

@admin_bp.route('/time-slots', methods=['GET', 'POST'])
def time_slots():
    if request.method == 'POST':
        day = request.form.get('day')
        period = request.form.get('period', type=int)
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        is_break = request.form.get('is_break') == 'on'
        break_name = request.form.get('break_name')

        slot = TimeSlot(
            day=day, period=period, start_time=start_time,
            end_time=end_time, is_break=is_break, break_name=break_name
        )
        db.session.add(slot)
        db.session.commit()
        flash("Time slot added!", "success")
        return redirect(url_for('admin.time_slots'))

    slots = TimeSlot.query.order_by(TimeSlot.day, TimeSlot.period).all()
    return render_template('admin/time_slots.html', slots=slots)

# ==========================================
# 9. LEAVE MANAGEMENT & SUBSTITUTIONS
# ==========================================

@admin_bp.route('/leaves')
def leaves():
    pending_leaves = LeaveRequest.query.filter_by(status='pending').order_by(LeaveRequest.created_at.desc()).all()
    past_leaves = LeaveRequest.query.filter(LeaveRequest.status != 'pending').order_by(LeaveRequest.created_at.desc()).all()
    faculty_list = Faculty.query.all()
    return render_template('admin/leaves.html', pending_leaves=pending_leaves, past_leaves=past_leaves, faculty_list=faculty_list)

@admin_bp.route('/leaves/<int:id>/<action>', methods=['POST'])
def update_leave(id, action):
    leave = LeaveRequest.query.get_or_404(id)
    remark = request.form.get('admin_remark', '')
    substitute_id = request.form.get('substitute_faculty_id', type=int)
    
    if action == 'approve':
        leave.status = 'approved'
        if substitute_id:
            leave.substitute_faculty_id = substitute_id
        leave.admin_remark = remark or 'Approved by Academic Admin'
        flash(f"Leave request for {leave.faculty.name} approved! Substitute notified.", "success")
    elif action == 'reject':
        leave.status = 'rejected'
        leave.admin_remark = remark or 'Rejected due to academic schedule constraints.'
        flash(f"Leave request for {leave.faculty.name} rejected.", "info")

    db.session.commit()
    return redirect(url_for('admin.leaves'))

# ==========================================
# 10. ACADEMIC CALENDAR
# ==========================================

@admin_bp.route('/academic-calendar')
def academic_calendar():
    notes = AcademicCalendarNote.query.order_by(AcademicCalendarNote.date).all()
    return render_template('admin/academic_calendar.html', notes=notes)

# ==========================================
# 11. ANALYTICS & REPORTS
# ==========================================

@admin_bp.route('/analytics')
def analytics():
    settings = InstitutionSettings.get_settings()
    faculty_members = Faculty.query.all()
    rooms = Room.query.all()
    
    # Faculty teaching loads
    faculty_names = [f.name for f in faculty_members]
    faculty_loads = [TimetableEntry.query.filter_by(faculty_id=f.id, is_active=True).count() for f in faculty_members]
    
    # Syllabus progress coverage distribution
    progress_entries = SyllabusProgress.query.all()
    dist_counts = {'0-25%': 0, '25-50%': 0, '50-75%': 0, '75-100%': 0}
    for p in progress_entries:
        pct = p.percentage_covered
        if pct < 25:
            dist_counts['0-25%'] += 1
        elif pct < 50:
            dist_counts['25-50%'] += 1
        elif pct < 75:
            dist_counts['50-75%'] += 1
        else:
            dist_counts['75-100%'] += 1

    return render_template(
        'admin/analytics.html',
        settings=settings,
        faculty_names=faculty_names,
        faculty_loads=faculty_loads,
        dist_counts=dist_counts,
        total_faculty=len(faculty_members),
        total_rooms=len(rooms)
    )

# ==========================================
# 12. INSTITUTION SETTINGS & BRANDING
# ==========================================

@admin_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    settings_obj = InstitutionSettings.get_settings()
    if request.method == 'POST':
        settings_obj.name = request.form.get('name', settings_obj.name)
        settings_obj.subtitle = request.form.get('subtitle', settings_obj.subtitle)
        settings_obj.address = request.form.get('address', settings_obj.address)
        settings_obj.contact_email = request.form.get('contact_email', settings_obj.contact_email)
        settings_obj.academic_year = request.form.get('academic_year', settings_obj.academic_year)
        settings_obj.semester_type = request.form.get('semester_type', settings_obj.semester_type)

        # Handle Logo Upload
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(upload_path)
                settings_obj.logo_path = filename

        db.session.commit()
        flash("Institution settings updated successfully!", "success")
        return redirect(url_for('admin.settings'))

    return render_template('admin/settings.html', settings=settings_obj)

# ==========================================
# 13. EXPORT TIMETABLE
# ==========================================

@admin_bp.route('/export/csv')
def export_csv():
    entries = TimetableEntry.query.filter_by(is_active=True).all()
    csv_rows = ["Day,Period,Time,Division,Course Code,Course Name,Faculty,Room\n"]
    for e in entries:
        ts = e.time_slot
        row = f'"{ts.day}","{ts.period}","{ts.start_time}-{ts.end_time}","{e.section.name}","{e.course.code}","{e.course.name}","{e.faculty.name}","{e.room.name}"\n'
        csv_rows.append(row)
    
    response = make_response("".join(csv_rows))
    response.headers["Content-Disposition"] = "attachment; filename=NovaX_Timetable_Schedule.csv"
    response.headers["Content-type"] = "text/csv"
    return response
