from datetime import datetime
from collections import defaultdict
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import (
    db, Section, Course, Room, TimeSlot,
    TimetableEntry, AcademicCalendarNote, InstitutionSettings
)
from . import student_bp
from .auth import role_required

@student_bp.before_request
@login_required
def student_before_request():
    pass

@student_bp.route('/')
@student_bp.route('/dashboard')
def dashboard():
    settings = InstitutionSettings.get_settings()
    # Default student section (e.g. SE - Computer A)
    sections = Section.query.all()
    selected_section_id = request.args.get('section_id', type=int)
    if not selected_section_id and sections:
        selected_section_id = sections[0].id
    
    current_section = Section.query.get(selected_section_id) if selected_section_id else None

    # Today's lectures for this section
    today_day = datetime.now().strftime('%A')
    all_entries = TimetableEntry.query.filter_by(section_id=selected_section_id, is_active=True).all() if selected_section_id else []
    
    today_entries = [e for e in all_entries if e.time_slot.day == today_day]
    today_entries.sort(key=lambda x: x.time_slot.period)

    # Next upcoming class
    next_class = today_entries[0] if today_entries else None

    # Public calendar announcements
    public_notes = AcademicCalendarNote.query.filter_by(is_public=True).order_by(AcademicCalendarNote.date).limit(5).all()

    return render_template(
        'student/dashboard.html',
        settings=settings,
        sections=sections,
        current_section=current_section,
        today_day=today_day,
        today_entries=today_entries,
        next_class=next_class,
        public_notes=public_notes
    )

@student_bp.route('/timetable')
def timetable():
    sections = Section.query.all()
    selected_section_id = request.args.get('section_id', type=int)
    if not selected_section_id and sections:
        selected_section_id = sections[0].id
    
    current_section = Section.query.get(selected_section_id) if selected_section_id else None

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    time_slots = TimeSlot.query.order_by(TimeSlot.period).all()
    
    seen_periods = set()
    periods = []
    for ts in time_slots:
        if ts.period not in seen_periods:
            seen_periods.add(ts.period)
            periods.append(ts)
    periods.sort(key=lambda x: x.period)

    entries = TimetableEntry.query.filter_by(section_id=selected_section_id, is_active=True).all() if selected_section_id else []
    grid = defaultdict(lambda: defaultdict(list))
    for e in entries:
        grid[e.time_slot.day][e.time_slot.period].append(e)

    return render_template(
        'student/timetable.html',
        sections=sections,
        current_section=current_section,
        days=days,
        periods=periods,
        grid=grid
    )

@student_bp.route('/academic-calendar')
def academic_calendar():
    return render_template('student/academic_calendar.html')
