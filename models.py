from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class BaseModel(db.Model):
    __abstract__ = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)


class User(UserMixin, BaseModel):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'admin', 'teacher', 'student'
    avatar_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    faculty_profile = db.relationship('Faculty', backref='user', uselist=False, cascade='all, delete-orphan')
    calendar_notes = db.relationship('AcademicCalendarNote', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
        
    def is_teacher(self):
        return self.role == 'teacher'
        
    def is_student(self):
        return self.role == 'student'

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Department(BaseModel):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(20), nullable=True)
    
    # Relationships
    faculty_members = db.relationship('Faculty', backref='department', lazy='dynamic', cascade='all, delete-orphan')
    courses = db.relationship('Course', backref='department', lazy='dynamic', cascade='all, delete-orphan')
    sections = db.relationship('Section', backref='department', lazy='dynamic', cascade='all, delete-orphan')
    elective_baskets = db.relationship('ElectiveBasket', backref='department', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Department {self.name}>"


class Faculty(BaseModel):
    __tablename__ = 'faculty'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), default='Assistant Professor')
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    short_code = db.Column(db.String(10), nullable=True)
    avatar_initials = db.Column(db.String(5), nullable=True)
    color_tag = db.Column(db.String(30), default='#3B82F6')
    max_hours_per_day = db.Column(db.Integer, default=4)
    max_hours_per_week = db.Column(db.Integer, default=18)
    preferred_days = db.Column(db.String(100), default='Monday,Tuesday,Wednesday,Thursday,Friday,Saturday')
    
    # Relationships
    timetable_entries = db.relationship('TimetableEntry', backref='faculty', lazy='dynamic')
    leave_requests = db.relationship('LeaveRequest', foreign_keys='LeaveRequest.faculty_id', backref='faculty', lazy='dynamic')
    substitution_requests = db.relationship('LeaveRequest', foreign_keys='LeaveRequest.substitute_faculty_id', backref='substitute_faculty', lazy='dynamic')
    syllabus_progress = db.relationship('SyllabusProgress', backref='faculty', lazy='dynamic')
    
    def get_initials(self):
        if self.avatar_initials:
            return self.avatar_initials
        parts = self.name.replace('Prof.', '').replace('Dr.', '').strip().split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        elif len(parts) == 1:
            return parts[0][:2].upper()
        return "FC"

    def __repr__(self):
        return f"<Faculty {self.name}>"


class Course(BaseModel):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)
    year = db.Column(db.Integer, default=2)  # 1, 2, 3, 4
    semester = db.Column(db.Integer, default=3)  # 1 to 8
    type = db.Column(db.String(30), default='theory')  # 'theory', 'lab', 'elective', 'project', 'extra'
    hours_per_week = db.Column(db.Integer, default=4)
    elective_basket_id = db.Column(db.Integer, db.ForeignKey('elective_baskets.id', ondelete='SET NULL'), nullable=True)
    color_code = db.Column(db.String(30), default='#6366F1')
    default_faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='SET NULL'), nullable=True)
    
    # Relationships
    timetable_entries = db.relationship('TimetableEntry', backref='course', lazy='dynamic')
    syllabus_progress = db.relationship('SyllabusProgress', backref='course', lazy='dynamic')
    default_faculty = db.relationship('Faculty', foreign_keys=[default_faculty_id])

    def __repr__(self):
        return f"<Course {self.code} - {self.name}>"


class Room(BaseModel):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False, unique=True)
    building = db.Column(db.String(60), default='Main Block')
    capacity = db.Column(db.Integer, default=60)
    type = db.Column(db.String(30), default='classroom')  # 'classroom', 'lab', 'auditorium', 'ground'
    is_available = db.Column(db.Boolean, default=True)
    
    # Relationships
    timetable_entries = db.relationship('TimetableEntry', backref='room', lazy='dynamic')

    def __repr__(self):
        return f"<Room {self.name} ({self.type})>"


class Section(BaseModel):
    __tablename__ = 'sections'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)  # e.g., 'SE - Computer A', 'BE - AI & DS'
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)
    year = db.Column(db.Integer, default=2)
    semester = db.Column(db.Integer, default=3)
    strength = db.Column(db.Integer, default=60)
    
    # Relationships
    timetable_entries = db.relationship('TimetableEntry', backref='section', lazy='dynamic')
    syllabus_progress = db.relationship('SyllabusProgress', backref='section', lazy='dynamic')

    def __repr__(self):
        return f"<Section {self.name}>"


class ElectiveBasket(BaseModel):
    __tablename__ = 'elective_baskets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)  # e.g., 'Elective Group 1 (Odd Sem)'
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)
    semester = db.Column(db.Integer, default=5)
    
    # Relationships
    courses = db.relationship('Course', backref='elective_basket', lazy='dynamic')
    timetable_entries = db.relationship('TimetableEntry', backref='elective_basket', lazy='dynamic')

    def __repr__(self):
        return f"<ElectiveBasket {self.name}>"


class TimeSlot(BaseModel):
    __tablename__ = 'time_slots'
    
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(20), nullable=False)  # 'Monday', 'Tuesday', ...
    period = db.Column(db.Integer, nullable=False)  # 1, 2, 3, ...
    start_time = db.Column(db.String(20), nullable=False)  # '09:00 AM'
    end_time = db.Column(db.String(20), nullable=False)    # '10:00 AM'
    is_break = db.Column(db.Boolean, default=False)
    break_name = db.Column(db.String(40), nullable=True)   # 'Short Break', 'Lunch Break'
    
    # Relationships
    timetable_entries = db.relationship('TimetableEntry', backref='time_slot', lazy='dynamic')

    def time_range_str(self):
        return f"{self.start_time} - {self.end_time}"

    def __repr__(self):
        return f"<TimeSlot {self.day} P{self.period} ({self.start_time}-{self.end_time})>"


class TimetableEntry(BaseModel):
    __tablename__ = 'timetable_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='CASCADE'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id', ondelete='CASCADE'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id', ondelete='CASCADE'), nullable=False)
    time_slot_id = db.Column(db.Integer, db.ForeignKey('time_slots.id', ondelete='CASCADE'), nullable=False)
    elective_basket_id = db.Column(db.Integer, db.ForeignKey('elective_baskets.id', ondelete='SET NULL'), nullable=True)
    version = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TimetableEntry Course:{self.course_id} Fac:{self.faculty_id} Room:{self.room_id} Slot:{self.time_slot_id}>"


class InstitutionSettings(BaseModel):
    __tablename__ = 'institution_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), default='ABC Engineering College')
    subtitle = db.Column(db.String(150), default='Pune, Maharashtra')
    logo_path = db.Column(db.String(255), default='logo.png')
    address = db.Column(db.String(255), default='Sector 10, Knowledge Park, Pune, Maharashtra 411001')
    contact_email = db.Column(db.String(120), default='contact@abc.edu')
    academic_year = db.Column(db.String(40), default='Academic Year: 2026–27')
    semester_type = db.Column(db.String(40), default='Odd Semester')
    quality_score = db.Column(db.Integer, default=92)
    constraints_satisfaction = db.Column(db.Integer, default=96)
    last_generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_settings(cls):
        settings = cls.query.first()
        if not settings:
            settings = cls(
                name='ABC Engineering College',
                subtitle='Pune, Maharashtra',
                logo_path='logo.png',
                address='Sector 10, Knowledge Park, Pune, Maharashtra 411001',
                contact_email='contact@abc.edu',
                academic_year='Academic Year: 2026–27',
                semester_type='Odd Semester',
                quality_score=92,
                constraints_satisfaction=96
            )
            db.session.add(settings)
            db.session.commit()
        return settings


class LeaveRequest(BaseModel):
    __tablename__ = 'leave_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='CASCADE'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    substitute_faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='SET NULL'), nullable=True)
    status = db.Column(db.String(30), default='pending')  # 'pending', 'approved', 'rejected'
    admin_remark = db.Column(db.Text, nullable=True)
    affected_classes_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<LeaveRequest Fac:{self.faculty_id} ({self.start_date} to {self.end_date}) [{self.status}]>"


class AcademicCalendarNote(BaseModel):
    __tablename__ = 'academic_calendar_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), default='academic')  # 'exam', 'holiday', 'event', 'note', 'deadline'
    color = db.Column(db.String(30), default='#6366F1')
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description or '',
            'start': self.date.isoformat(),
            'end': self.end_date.isoformat() if self.end_date else self.date.isoformat(),
            'category': self.category,
            'backgroundColor': self.color or '#6366F1',
            'borderColor': self.color or '#6366F1',
            'is_public': self.is_public,
            'created_by': self.author.username if self.author else 'System'
        }


class SyllabusProgress(BaseModel):
    __tablename__ = 'syllabus_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='CASCADE'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id', ondelete='CASCADE'), nullable=False)
    percentage_covered = db.Column(db.Integer, default=0)
    topics_covered = db.Column(db.Text, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SyllabusProgress Course:{self.course_id} Fac:{self.faculty_id} {self.percentage_covered}%>"
