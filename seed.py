import os
from datetime import datetime, date, timedelta
from app import create_app
from models import (
    db, User, Department, Faculty, Course, Room, Section,
    ElectiveBasket, TimeSlot, TimetableEntry, InstitutionSettings,
    LeaveRequest, AcademicCalendarNote, SyllabusProgress
)

def seed_database():
    app = create_app()
    with app.app_context():
        print("[*] Resetting and Seeding NovaX Database...")
        db.drop_all()
        db.create_all()

        # 1. Institution Settings
        settings = InstitutionSettings(
            name='ABC Engineering College',
            subtitle='Pune, Maharashtra',
            logo_path='logo.png',
            address='Sector 10, Knowledge Park, Pune, Maharashtra 411001',
            contact_email='contact@abc.edu',
            academic_year='Academic Year: 2026–27',
            semester_type='Odd Semester',
            quality_score=92,
            constraints_satisfaction=96,
            last_generated_at=datetime(2026, 8, 16, 12, 30)
        )
        db.session.add(settings)

        # 2. Users (Admin, Teachers, Student)
        admin_user = User(username='Admin', email='admin@novax.edu', role='admin')
        admin_user.set_password('admin123')
        db.session.add(admin_user)

        student_user = User(username='John Student', email='student@novax.edu', role='student')
        student_user.set_password('student123')
        db.session.add(student_user)

        # 3. Departments
        dept_comp = Department(name='Computer Engineering', code='COMP')
        dept_it = Department(name='Information Technology', code='IT')
        dept_aids = Department(name='AI & Data Science', code='AIDS')
        dept_ash = Department(name='Applied Sciences', code='ASH')
        db.session.add_all([dept_comp, dept_it, dept_aids, dept_ash])
        db.session.flush()

        # 4. Faculty Members
        faculty_data = [
            ('Prof. Sharma', 'sharma@novax.edu', dept_ash.id, 'Associate Professor', 'MAT101', 'PS', '#3b82f6', 4, 18),
            ('Prof. Patel', 'patel@novax.edu', dept_ash.id, 'Assistant Professor', 'MAT102', 'PP', '#10b981', 4, 18),
            ('Prof. Khan', 'khan@novax.edu', dept_ash.id, 'Assistant Professor', 'PHY101', 'PK', '#a855f7', 4, 18),
            ('Prof. Verma', 'verma@novax.edu', dept_ash.id, 'Assistant Professor', 'PHY102', 'PV', '#f97316', 4, 18),
            ('Prof. Iyer', 'iyer@novax.edu', dept_comp.id, 'Associate Professor', 'CSE101', 'PI', '#ec4899', 4, 18),
            ('Prof. R. Shah', 'shah@novax.edu', dept_comp.id, 'Assistant Professor', 'CSE102', 'RS', '#eab308', 4, 18),
            ('Prof. S. Joshi', 'joshi@novax.edu', dept_comp.id, 'Assistant Professor', 'CSE103', 'SJ', '#14b8a6', 4, 18),
            ('Prof. P. Kulkarni', 'kulkarni@novax.edu', dept_ash.id, 'Assistant Professor', 'MAT103', 'PK', '#6366f1', 4, 18),
            ('Prof. M. Verma', 'mverma@novax.edu', dept_comp.id, 'Assistant Professor', 'CSE104', 'MV', '#f43f5e', 4, 18),
            ('Prof. A. Patil', 'apatil@novax.edu', dept_comp.id, 'Assistant Professor', 'CSE105', 'AP', '#06b6d4', 4, 18),
            ('Prof. K. Singh', 'ksingh@novax.edu', dept_comp.id, 'Assistant Professor', 'CSE106', 'KS', '#8b5cf6', 4, 18),
            ('Prof. A. Deshpande', 'adeshpande@novax.edu', dept_aids.id, 'Professor', 'CSE201', 'AD', '#3b82f6', 4, 18),
            ('Prof. V. Khot', 'vkhot@novax.edu', dept_it.id, 'Assistant Professor', 'CSE202', 'VK', '#10b981', 4, 18),
            ('Prof. N. Jain', 'njain@novax.edu', dept_it.id, 'Assistant Professor', 'CSE203', 'NJ', '#eab308', 4, 18),
            ('Prof. P. More', 'pmore@novax.edu', dept_aids.id, 'Assistant Professor', 'CSE204', 'PM', '#ec4899', 4, 18),
            ('Prof. S. Bansal', 'sbansal@novax.edu', dept_aids.id, 'Assistant Professor', 'CSE205', 'SB', '#14b8a6', 4, 18),
            ('Prof. Various', 'various@novax.edu', dept_comp.id, 'Guest Lecturer', 'GEN101', 'PV', '#64748b', 4, 18)
        ]

        faculty_objs = {}
        for name, email, dept_id, desig, code, init, color, max_d, max_w in faculty_data:
            # Create user account for faculty
            u = User(username=name, email=email, role='teacher')
            u.set_password('teacher123')
            db.session.add(u)
            db.session.flush()

            f = Faculty(
                user_id=u.id,
                name=name,
                email=email,
                department_id=dept_id,
                designation=desig,
                short_code=code,
                avatar_initials=init,
                color_tag=color,
                max_hours_per_day=max_d,
                max_hours_per_week=max_w
            )
            db.session.add(f)
            db.session.flush()
            faculty_objs[name] = f

        # 5. Rooms & Labs (matching Ref Image 2)
        rooms_data = [
            ('R-201', 'Main Academic Block', 60, 'classroom'),
            ('R-202', 'Main Academic Block', 60, 'classroom'),
            ('R-203', 'Main Academic Block', 60, 'classroom'),
            ('R-301', 'North Wing', 60, 'classroom'),
            ('R-302', 'North Wing', 60, 'classroom'),
            ('R-303', 'North Wing', 60, 'classroom'),
            ('Lab-1', 'Computing Center', 35, 'lab'),
            ('Lab-2', 'Computing Center', 35, 'lab'),
            ('Lab-3', 'AI Research Wing', 35, 'lab'),
            ('Library', 'Central Block', 120, 'classroom'),
            ('Ground', 'Sports Complex', 200, 'classroom'),
            ('Auditorium', 'Main Academic Block', 300, 'auditorium')
        ]

        room_objs = {}
        for r_name, r_bld, r_cap, r_type in rooms_data:
            r = Room(name=r_name, building=r_bld, capacity=r_cap, type=r_type)
            db.session.add(r)
            db.session.flush()
            room_objs[r_name] = r

        # 6. Sections / Divisions (matching Ref Image 2)
        sec_comp_a = Section(name='SE - Computer A', department_id=dept_comp.id, year=2, semester=3, strength=60)
        sec_comp_b = Section(name='SE - Computer B', department_id=dept_comp.id, year=2, semester=3, strength=60)
        sec_te_comp = Section(name='TE - Computer A', department_id=dept_comp.id, year=3, semester=5, strength=60)
        sec_be_aids = Section(name='BE - AI & DS', department_id=dept_aids.id, year=4, semester=7, strength=60)
        db.session.add_all([sec_comp_a, sec_comp_b, sec_te_comp, sec_be_aids])
        db.session.flush()

        # 7. Elective Baskets
        basket_1 = ElectiveBasket(name='Elective Group 1', department_id=dept_comp.id, semester=5)
        basket_2 = ElectiveBasket(name='Elective Group 2', department_id=dept_comp.id, semester=5)
        db.session.add_all([basket_1, basket_2])
        db.session.flush()

        # 8. Courses
        courses_data = [
            ('DSA', 'CS301', 'DSA', dept_comp.id, 2, 3, 'theory', 4, None, faculty_objs['Prof. A. Patil'].id),
            ('DBMS', 'CS302', 'DBMS', dept_comp.id, 2, 3, 'theory', 4, None, faculty_objs['Prof. R. Shah'].id),
            ('Maths-III', 'MA301', 'Maths-III', dept_ash.id, 2, 3, 'theory', 4, None, faculty_objs['Prof. P. Kulkarni'].id),
            ('OOP', 'CS303', 'OOP', dept_comp.id, 2, 3, 'theory', 4, None, faculty_objs['Prof. S. Joshi'].id),
            ('CN', 'CS304', 'CN', dept_comp.id, 2, 3, 'theory', 4, None, faculty_objs['Prof. M. Verma'].id),
            ('OS', 'CS305', 'OS', dept_comp.id, 2, 3, 'theory', 3, None, faculty_objs['Prof. K. Singh'].id),
            ('Mini Project', 'CS306', 'Mini Project', dept_comp.id, 2, 3, 'lab', 3, None, faculty_objs['Prof. A. Patil'].id),
            ('OS Project', 'CS307', 'OS Project', dept_comp.id, 2, 3, 'lab', 2, None, faculty_objs['Prof. K. Singh'].id),
            ('Library', 'GEN01', 'Library', dept_comp.id, 2, 3, 'extra', 2, None, faculty_objs['Prof. Various'].id),
            ('Sports', 'GEN02', 'Sports', dept_comp.id, 2, 3, 'extra', 1, None, faculty_objs['Prof. Various'].id),
            ('Mentoring', 'GEN03', 'Mentoring', dept_comp.id, 2, 3, 'extra', 2, None, faculty_objs['Prof. R. Shah'].id),
            ('Activity', 'GEN04', 'Activity', dept_comp.id, 2, 3, 'extra', 1, None, faculty_objs['Prof. Various'].id),
            ('Seminar', 'GEN05', 'Seminar', dept_comp.id, 2, 3, 'extra', 1, None, faculty_objs['Prof. Various'].id),
            # Elective Group 1
            ('Machine Learning', 'CS501', 'Machine Learning', dept_comp.id, 3, 5, 'elective', 3, basket_1.id, faculty_objs['Prof. A. Deshpande'].id),
            ('Cyber Security', 'CS502', 'Cyber Security', dept_comp.id, 3, 5, 'elective', 3, basket_1.id, faculty_objs['Prof. V. Khot'].id),
            ('Cloud Computing', 'CS503', 'Cloud Computing', dept_comp.id, 3, 5, 'elective', 3, basket_1.id, faculty_objs['Prof. N. Jain'].id),
            # Elective Group 2
            ('NLP', 'CS504', 'NLP', dept_comp.id, 3, 5, 'elective', 3, basket_2.id, faculty_objs['Prof. P. More'].id),
            ('Computer Vision', 'CS505', 'Computer Vision', dept_comp.id, 3, 5, 'elective', 3, basket_2.id, faculty_objs['Prof. S. Bansal'].id),
            ('Blockchain', 'CS506', 'Blockchain', dept_comp.id, 3, 5, 'elective', 3, basket_2.id, faculty_objs['Prof. Iyer'].id),
        ]

        course_objs = {}
        for short_name, code, title, dept_id, yr, sem, c_type, hrs, b_id, f_id in courses_data:
            c = Course(
                code=code,
                name=title,
                department_id=dept_id,
                year=yr,
                semester=sem,
                type=c_type,
                hours_per_week=hrs,
                elective_basket_id=b_id,
                default_faculty_id=f_id
            )
            db.session.add(c)
            db.session.flush()
            course_objs[short_name] = c

        # 9. Time Slots (P1 to P9 with Short Break & Lunch Break matching Ref Image 2)
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        slots_template = [
            (1, '09:00', '10:00', False, None),
            (2, '10:00', '11:00', False, None),
            (3, '11:00', '11:15', True, 'Short Break'),
            (4, '11:15', '12:15', False, None),
            (5, '12:15', '01:15', False, None),
            (6, '01:15', '02:00', True, 'Lunch Break'),
            (7, '02:00', '03:00', False, None),
            (8, '03:00', '04:00', False, None),
            (9, '04:00', '05:00', False, None)
        ]

        slot_objs = {}
        for day in days:
            for period, st, et, is_b, b_name in slots_template:
                ts = TimeSlot(
                    day=day,
                    period=period,
                    start_time=st,
                    end_time=et,
                    is_break=is_b,
                    break_name=b_name
                )
                db.session.add(ts)
                db.session.flush()
                slot_objs[(day, period)] = ts

        # 10. Pre-Populate Reference Timetable for 'SE - Computer A' (matching Ref Image 2 perfectly!)
        schedule_matrix = [
            # Period 1 (09:00 - 10:00)
            ('Monday', 1, 'DSA', 'Prof. A. Patil', 'R-201'),
            ('Tuesday', 1, 'DBMS', 'Prof. R. Shah', 'R-202'),
            ('Wednesday', 1, 'Maths-III', 'Prof. P. Kulkarni', 'R-203'),
            ('Thursday', 1, 'OOP', 'Prof. S. Joshi', 'R-201'),
            ('Friday', 1, 'CN', 'Prof. M. Verma', 'R-203'),
            ('Saturday', 1, 'Mini Project', 'Prof. A. Patil', 'Lab-2'),

            # Period 2 (10:00 - 11:00)
            ('Monday', 2, 'DBMS', 'Prof. R. Shah', 'R-202'),
            ('Tuesday', 2, 'DSA', 'Prof. A. Patil', 'R-201'),
            ('Wednesday', 2, 'CN', 'Prof. M. Verma', 'R-203'),
            ('Thursday', 2, 'DSA', 'Prof. A. Patil', 'R-202'),
            ('Friday', 2, 'Maths-III', 'Prof. P. Kulkarni', 'R-201'),
            ('Saturday', 2, 'Library', 'Prof. Various', 'Library'),

            # Period 4 (11:15 - 12:15)
            ('Monday', 4, 'OOP', 'Prof. S. Joshi', 'R-201'),
            ('Tuesday', 4, 'OOP', 'Prof. S. Joshi', 'R-201'),
            ('Wednesday', 4, 'DBMS', 'Prof. R. Shah', 'R-202'),
            ('Thursday', 4, 'Maths-III', 'Prof. P. Kulkarni', 'R-203'),
            ('Friday', 4, 'DSA', 'Prof. A. Patil', 'R-201'),
            ('Saturday', 4, 'Machine Learning', 'Prof. A. Deshpande', 'R-301'),

            # Period 5 (12:15 - 01:15)
            ('Monday', 5, 'Maths-III', 'Prof. P. Kulkarni', 'R-203'),
            ('Tuesday', 5, 'Machine Learning', 'Prof. A. Deshpande', 'R-301'),
            ('Wednesday', 5, 'OOP', 'Prof. S. Joshi', 'R-201'),
            ('Thursday', 5, 'DBMS', 'Prof. R. Shah', 'R-202'),
            ('Friday', 5, 'Cyber Security', 'Prof. V. Khot', 'R-302'),
            ('Saturday', 5, 'OS', 'Prof. K. Singh', 'Lab-1'),

            # Period 7 (02:00 - 03:00)
            ('Monday', 7, 'OS', 'Prof. K. Singh', 'Lab-1'),
            ('Tuesday', 7, 'CN', 'Prof. M. Verma', 'R-203'),
            ('Wednesday', 7, 'NLP', 'Prof. P. More', 'R-301'),
            ('Thursday', 7, 'CN', 'Prof. M. Verma', 'R-203'),
            ('Friday', 7, 'OS', 'Prof. K. Singh', 'Lab-1'),

            # Period 8 (03:00 - 04:00)
            ('Monday', 8, 'Mini Project', 'Prof. A. Patil', 'Lab-2'),
            ('Tuesday', 8, 'OS Project', 'Prof. K. Singh', 'Lab-1'),
            ('Wednesday', 8, 'DSA', 'Prof. A. Patil', 'R-201'),
            ('Thursday', 8, 'Mini Project', 'Prof. A. Patil', 'Lab-2'),
            ('Friday', 8, 'Seminar', 'Prof. Various', 'R-201'),

            # Period 9 (04:00 - 05:00)
            ('Monday', 9, 'Mentoring', 'Prof. R. Shah', 'R-201'),
            ('Tuesday', 9, 'Sports', 'Prof. Various', 'Ground'),
            ('Wednesday', 9, 'Library', 'Prof. Various', 'Library'),
            ('Thursday', 9, 'Mentoring', 'Prof. R. Shah', 'R-201'),
            ('Friday', 9, 'Activity', 'Prof. Various', 'R-201')
        ]

        for day, period, c_name, f_name, r_name in schedule_matrix:
            c = course_objs.get(c_name)
            f = faculty_objs.get(f_name)
            r = room_objs.get(r_name)
            ts = slot_objs.get((day, period))

            if c and f and r and ts:
                entry = TimetableEntry(
                    course_id=c.id,
                    faculty_id=f.id,
                    room_id=r.id,
                    section_id=sec_comp_a.id,
                    time_slot_id=ts.id,
                    elective_basket_id=c.elective_basket_id,
                    version=3,
                    is_active=True
                )
                db.session.add(entry)

        # 11. Pre-Seed Leave Requests & Substitutions (matching Ref Image 1)
        leave1 = LeaveRequest(
            faculty_id=faculty_objs['Prof. Sharma'].id,
            start_date=date.today() + timedelta(days=2),
            end_date=date.today() + timedelta(days=2),
            reason='Attending National Mathematics Curriculum Conclave',
            substitute_faculty_id=faculty_objs['Prof. Patel'].id,
            status='approved',
            admin_remark='Automated backup substitution confirmed by Admin'
        )
        leave2 = LeaveRequest(
            faculty_id=faculty_objs['Prof. Khan'].id,
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=6),
            reason='Medical Consultation & Review',
            substitute_faculty_id=faculty_objs['Prof. Verma'].id,
            status='pending'
        )
        db.session.add_all([leave1, leave2])

        # 12. Pre-Seed Academic Calendar Notes & Events
        cal_notes = [
            (date.today() + timedelta(days=10), date.today() + timedelta(days=12), 'Mid-Term Unit Test 1', 'Continuous Internal Assessment for all second and third year engineering branches.', 'exam', '#EF4444', True),
            (date.today() + timedelta(days=18), date.today() + timedelta(days=20), 'Innovision 2026 – Annual Tech Fest', 'Hackathon, Project Expo, and AI Symposium in Auditorium.', 'event', '#10B981', True),
            (date.today() + timedelta(days=25), None, 'Mini Project Milestone 1 Review', 'Submission of System Architecture and ER Diagrams in Lab-2.', 'deadline', '#F59E0B', True),
            (date.today() + timedelta(days=32), None, 'Faculty Development Workshop on LLM Engineering', 'Guest lecture by Industry Expert Dr. Mehta.', 'event', '#6366F1', False)
        ]

        for s_date, e_date, title, desc, cat, color, is_pub in cal_notes:
            note = AcademicCalendarNote(
                date=s_date,
                end_date=e_date,
                title=title,
                description=desc,
                category=cat,
                color=color,
                is_public=is_pub,
                created_by_user_id=admin_user.id
            )
            db.session.add(note)

        # 13. Pre-Seed Syllabus Progress for Faculty
        progress_seeds = [
            ('DSA', 'Prof. A. Patil', sec_comp_a.id, 65, 'Arrays, Linked Lists, Stacks & Queues, Trees Completed'),
            ('DBMS', 'Prof. R. Shah', sec_comp_a.id, 55, 'Relational Algebra, SQL, Normalization (1NF-3NF) Completed'),
            ('Maths-III', 'Prof. P. Kulkarni', sec_comp_a.id, 70, 'Fourier Transforms & Partial Differential Equations Completed'),
            ('OOP', 'Prof. S. Joshi', sec_comp_a.id, 60, 'Classes, Inheritance, Polymorphism & Exception Handling Completed'),
            ('CN', 'Prof. M. Verma', sec_comp_a.id, 45, 'OSI Model, TCP/IP & Data Link Layer Protocols Completed'),
            ('OS', 'Prof. K. Singh', sec_comp_a.id, 50, 'Process Scheduling, Synchronization & Deadlocks Completed')
        ]

        for c_name, f_name, s_id, pct, topics in progress_seeds:
            c = course_objs.get(c_name)
            f = faculty_objs.get(f_name)
            if c and f:
                sp = SyllabusProgress(
                    course_id=c.id,
                    faculty_id=f.id,
                    section_id=s_id,
                    percentage_covered=pct,
                    topics_covered=topics
                )
                db.session.add(sp)

        db.session.commit()
        print("[OK] NovaX Database successfully seeded with rich realistic college data!")

if __name__ == '__main__':
    seed_database()
