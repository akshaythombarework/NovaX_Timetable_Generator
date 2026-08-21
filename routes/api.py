from datetime import datetime, date
from flask import request, jsonify
from flask_login import current_user, login_required
from models import db, AcademicCalendarNote, Faculty, TimeSlot, TimetableEntry, SyllabusProgress
from generator.algorithm import find_substitute_recommendations
from . import api_bp

@api_bp.route('/calendar/events', methods=['GET'])
def get_calendar_events():
    query = AcademicCalendarNote.query
    if not current_user.is_authenticated or current_user.role == 'student':
        query = query.filter_by(is_public=True)
    
    notes = query.all()
    return jsonify([n.to_dict() for n in notes])

@api_bp.route('/calendar/events', methods=['POST'])
@login_required
def create_calendar_event():
    data = request.get_json() or {}
    title = data.get('title')
    start_str = data.get('start')
    end_str = data.get('end')
    description = data.get('description', '')
    category = data.get('category', 'academic')
    color = data.get('color', '#6366F1')
    is_public = bool(data.get('is_public', True))

    if not title or not start_str:
        return jsonify({'error': 'Title and Start Date are required'}), 400

    try:
        start_date = datetime.strptime(start_str[:10], '%Y-%m-%d').date()
        end_date = datetime.strptime(end_str[:10], '%Y-%m-%d').date() if end_str else start_date
    except Exception as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400

    note = AcademicCalendarNote(
        title=title,
        date=start_date,
        end_date=end_date,
        description=description,
        category=category,
        color=color,
        is_public=is_public,
        created_by_user_id=current_user.id
    )
    db.session.add(note)
    db.session.commit()
    return jsonify({'success': True, 'event': note.to_dict()})

@api_bp.route('/calendar/events/<int:id>', methods=['DELETE'])
@login_required
def delete_calendar_event(id):
    note = AcademicCalendarNote.query.get_or_404(id)
    if not current_user.is_admin() and note.created_by_user_id != current_user.id:
        return jsonify({'error': 'Unauthorized to delete this note'}), 403

    db.session.delete(note)
    db.session.commit()
    return jsonify({'success': True})

@api_bp.route('/substitute/calculate', methods=['POST'])
@login_required
def calculate_substitutes():
    data = request.get_json() or {}
    faculty_id = data.get('faculty_id')
    date_str = data.get('date')

    if not faculty_id:
        return jsonify({'error': 'faculty_id is required'}), 400

    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
    except Exception:
        target_date = date.today()

    result = find_substitute_recommendations(int(faculty_id), target_date)
    
    # Serialize for JSON
    serialized_classes = []
    for item in result['affected_classes']:
        rec = item['recommended_substitute']
        rec_data = None
        if rec:
            f = rec['faculty']
            rec_data = {
                'id': f.id,
                'name': f.name,
                'initials': f.get_initials(),
                'color_tag': f.color_tag or '#3B82F6',
                'reason': rec['reason'],
                'workload': rec['workload']
            }
        
        backup2 = item['backup_substitute_2']
        backup2_data = None
        if backup2:
            f2 = backup2['faculty']
            backup2_data = {
                'id': f2.id,
                'name': f2.name,
                'initials': f2.get_initials(),
                'reason': backup2['reason'],
                'workload': backup2['workload']
            }

        serialized_classes.append({
            'entry_id': item['entry_id'],
            'time': item['time'],
            'class_division': item['class_division'],
            'subject': item['subject'],
            'course_code': item['course_code'],
            'room': item['room'],
            'recommended_substitute': rec_data,
            'backup_substitute_2': backup2_data
        })

    return jsonify({
        'success': True,
        'faculty_name': result['faculty'].name,
        'date_formatted': result['date'],
        'day': result['day'],
        'affected_count': result['affected_count'],
        'affected_classes': serialized_classes
    })

@api_bp.route('/syllabus/update-quick', methods=['POST'])
@login_required
def update_syllabus_quick():
    data = request.get_json() or {}
    record_id = data.get('id')
    percentage = data.get('percentage')

    if record_id is not None and percentage is not None:
        rec = SyllabusProgress.query.get(int(record_id))
        if rec:
            rec.percentage_covered = int(percentage)
            db.session.commit()
            return jsonify({'success': True, 'percentage': rec.percentage_covered})
            
    return jsonify({'error': 'Invalid request'}), 400
