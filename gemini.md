```markdown
# Automated Timetable Generator – Complete Guide & AI Prompts

## 1. Project Overview

A web-based platform to automatically generate clash-free timetables for colleges considering:
- Faculty teaching load
- Room availability & type
- Elective subject grouping
- Section clashes
- Lunch breaks / working days

Additional features:
- Role-based login (Admin, Teacher, Student)
- Teacher leave management with substitute suggestion
- Automatic email to substitute teacher
- Institution branding (logo & name)
- Academic calendar with teacher notes
- Analytics dashboards (teacher & admin)
- Syllabus coverage tracking
- Metallic chic UI with animations

## 2. Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python + Flask |
| Database | SQLite (dev) / MySQL (prod) |
| ORM | Flask-SQLAlchemy |
| Auth | Flask-Login |
| Email | Flask-Mail (or smtplib) |
| Frontend | HTML, CSS, Bootstrap 5, Jinja2 |
| Animations | CSS Keyframes + AOS (Animate On Scroll) + GSAP (optional) |
| Charts | Chart.js |
| Calendar | FullCalendar.js |
| Icons | Font Awesome |

## 3. File Structure

```
timetable-generator/
├── app.py
├── config.py
├── models.py
├── requirements.txt
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── admin.py
│   ├── teacher.py
│   └── student.py
├── generator/
│   ├── __init__.py
│   └── algorithm.py
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── courses.html
│   │   ├── faculty.html
│   │   ├── rooms.html
│   │   ├── sections.html
│   │   ├── elective_baskets.html
│   │   ├── timetable.html
│   │   ├── leaves.html
│   │   ├── settings.html
│   │   ├── academic_calendar.html
│   │   └── analytics.html
│   ├── teacher/
│   │   ├── dashboard.html
│   │   ├── apply_leave.html
│   │   ├── academic_calendar.html
│   │   └── syllabus_progress.html
│   └── student/
│       ├── dashboard.html
│       └── academic_calendar.html
├── static/
│   ├── css/
│   │   ├── style.css
│   │   └── animations.css
│   ├── js/
│   │   ├── main.js
│   │   └── calendar.js
│   └── uploads/          # For logo
└── database.db
```

## 4. Database Schema

### Users
| Column | Type |
|--------|------|
| id | Integer PK |
| username | String unique |
| email | String unique |
| password_hash | String |
| role | String (admin/teacher/student) |
| created_at | DateTime |

### Departments
| Column | Type |
|--------|------|
| id | Integer PK |
| name | String |

### Faculty
| Column | Type |
|--------|------|
| id | Integer PK |
| user_id | FK users |
| department_id | FK departments |
| name | String |
| max_hours_per_day | Integer |
| max_hours_per_week | Integer |
| preferred_days | String (optional) |

### Courses
| Column | Type |
|--------|------|
| id | Integer PK |
| code | String |
| name | String |
| department_id | FK departments |
| year | Integer |
| semester | Integer |
| type | String (theory/lab/elective) |
| hours_per_week | Integer |
| elective_basket_id | FK elective_baskets (nullable) |

### Rooms
| Column | Type |
|--------|------|
| id | Integer PK |
| name | String |
| capacity | Integer |
| type | String (classroom/lab) |

### Sections
| Column | Type |
|--------|------|
| id | Integer PK |
| name | String |
| department_id | FK departments |
| year | Integer |
| semester | Integer |
| strength | Integer |

### ElectiveBaskets
| Column | Type |
|--------|------|
| id | Integer PK |
| name | String |
| department_id | FK departments |
| semester | Integer |

### TimeSlots
| Column | Type |
|--------|------|
| id | Integer PK |
| day | String |
| period | Integer |
| start_time | String |
| end_time | String |
| is_break | Boolean |

### TimetableEntries
| Column | Type |
|--------|------|
| id | Integer PK |
| course_id | FK courses |
| faculty_id | FK faculty |
| room_id | FK rooms |
| section_id | FK sections |
| time_slot_id | FK time_slots |
| elective_basket_id | FK elective_baskets (nullable) |
| created_at | DateTime |

### InstitutionSettings
| Column | Type |
|--------|------|
| id | Integer PK |
| name | String |
| logo_path | String |
| address | String |
| contact_email | String |
| updated_at | DateTime |

### LeaveRequests
| Column | Type |
|--------|------|
| id | Integer PK |
| faculty_id | FK faculty |
| start_date | Date |
| end_date | Date |
| reason | Text |
| substitute_faculty_id | FK faculty |
| status | String (pending/approved/rejected) |
| admin_remark | Text |
| created_at | DateTime |

### AcademicCalendarNotes
| Column | Type |
|--------|------|
| id | Integer PK |
| date | Date |
| title | String |
| description | Text |
| created_by_user_id | FK users |
| is_public | Boolean |
| created_at | DateTime |

### SyllabusProgress
| Column | Type |
|--------|------|
| id | Integer PK |
| course_id | FK courses |
| faculty_id | FK faculty |
| section_id | FK sections |
| percentage_covered | Integer |
| last_updated | DateTime |

## 5. Metallic Chic UI & Animations Guidelines

### Color Palette
- Base: dark charcoal `#1a1a1a`
- Metal gradients: `linear-gradient(145deg, #d4d4d4, #f0f0f0, #b0b0b0)`
- Accent: chrome silver `#c0c0c0`, brushed steel `#888`, gold highlights `#d4af37`
- Text: white on dark, black on light metallic panels.

### Typography
- Headings: 'Playfair Display' or 'Montserrat'
- Body: 'Poppins' or 'Inter'
- Use letter-spacing for a premium feel.

### Components
- Cards: glassmorphism with `backdrop-filter: blur(10px)` and metallic borders.
- Buttons: gradient metal backgrounds with 3D effect using box-shadow.
- Navbar: dark glass with metallic logo.
- Tables: striped with hover effects, subtle shadows.

### Animations
- Fade-in on page load using CSS `@keyframes fadeIn`.
- Slide-up for cards.
- Hover effects: scale + shadow.
- Loading spinners with metallic ring.
- Use AOS (Animate On Scroll) library for section reveals.
- FullCalendar events can have custom colors (gold, silver).

Add the following to `animations.css`:

```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.fade-in { animation: fadeIn 0.6s ease-in; }

@keyframes slideUp {
  from { transform: translateY(30px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.slide-up { animation: slideUp 0.5s ease-out; }

/* Metallic button */
.btn-metal {
  background: linear-gradient(145deg, #e0e0e0, #cfcfcf);
  border: 1px solid #aaa;
  color: #222;
  text-shadow: 0 1px 0 #fff;
  box-shadow: 0 4px 8px rgba(0,0,0,0.3);
  transition: all 0.2s ease;
}
.btn-metal:hover {
  background: linear-gradient(145deg, #f5f5f5, #d0d0d0);
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.4);
}

/* Glass card */
.glass-card {
  background: rgba(255,255,255,0.08);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}
```

## 6. Step-by-Step AI Prompts for Antigravity IDE

### Step 1: Project Setup
**Prompt:**
> Create a Flask project with the following structure: app.py, config.py, models.py, requirements.txt, routes/__init__.py, routes/auth.py, routes/admin.py, routes/teacher.py, routes/student.py, generator/algorithm.py. Initialize Flask app, SQLAlchemy, Flask-Login, Flask-Mail. Add a basic home route. Include a config.py with SECRET_KEY, SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db', MAIL settings (use dummy values for now). Include requirements.txt with Flask, Flask-SQLAlchemy, Flask-Login, Flask-Mail, Werkzeug.

### Step 2: Database Models
**Prompt:**
> In models.py, define all tables described in Section 4 (Users, Departments, Faculty, Courses, Rooms, Sections, ElectiveBaskets, TimeSlots, TimetableEntries, InstitutionSettings, LeaveRequests, AcademicCalendarNotes, SyllabusProgress). Use SQLAlchemy. Include relationships (e.g., faculty.user, faculty.department, course.department, etc.). Add appropriate backrefs. Use date and datetime types where needed.

### Step 3: Authentication (Login/Logout)
**Prompt:**
> Implement role-based login in routes/auth.py. Create a login page (GET/POST) that accepts username/email and password, and a role dropdown (Admin/Teacher/Student). Use Flask-Login's UserMixin on the User model. Hash passwords with werkzeug.security. On successful login, redirect based on role: admin to /admin/dashboard, teacher to /teacher/dashboard, student to /student/dashboard. Add logout route. Create a base template (base.html) that includes navbar, flash messages, and links to logout. Use Bootstrap 5 and include the metallic CSS from static/css/style.css. Add a simple login.html template.

### Step 4: Admin CRUD (Departments, Faculty, Rooms, Sections, Courses, Elective Baskets)
**Prompt:**
> Create admin routes for managing Departments, Faculty, Rooms, Sections, Courses, and Elective Baskets. Each should have list view, add form, edit form, delete action. Use Flask-WTF or manual forms (simpler). All routes must require admin role. Provide templates for each (list + form). Keep UI consistent with metallic theme. Use flash messages for success/error.

### Step 5: Timetable Generation Algorithm
**Prompt:**
> Implement the timetable generation algorithm in generator/algorithm.py. The function should take all relevant data (courses, sections, faculty, rooms, time slots) and return a list of TimetableEntries or None if impossible. Use backtracking with hard constraints:
> - No faculty, room, or section clash at same time slot.
> - Lab courses must use lab rooms.
> - Elective basket courses for a section must be scheduled in parallel (same time slot) for different electives within the basket.
> - Room capacity >= section strength.
> - Faculty max hours per day/week not exceeded.
> Start with greedy assignment, then backtrack if needed. The function should be callable from an admin route. Include comments explaining logic.

### Step 6: Admin Timetable View & Generation Trigger
**Prompt:**
> Add an admin route `/admin/generate` (POST) that calls the timetable generation function, deletes existing timetable entries, and creates new ones. If generation fails, show error. Add `/admin/timetable` (GET) to display the timetable in a grid (days vs periods) with course, faculty, room, section. Include edit/delete buttons for each entry. The edit form should allow changing faculty, room, or time slot manually. Use FullCalendar or a custom table grid.

### Step 7: Institution Settings (Logo & Name)
**Prompt:**
> Create an admin settings page (`/admin/settings`) with a form to update institution name, address, contact email, and upload logo. Use Flask-Uploads or simple file handling to save logo in static/uploads/. Store settings in InstitutionSettings table. The base template should display the logo and name in the navbar and in all pages. Add a default logo if none set.

### Step 8: Leave Management & Substitute Suggestion
**Prompt:**
> Implement leave management:
> - Teacher route `/teacher/apply-leave` (GET/POST): form with start_date, end_date, reason, substitute_faculty_id (dropdown of other faculty). Save with status 'pending'.
> - Admin route `/admin/leaves` (GET): list all leave requests with status. Approve/reject buttons.
> - When admin approves, set status='approved' and send email to substitute faculty using Flask-Mail. Email subject: 'Substitute Teaching Request', body includes date, course, room, and original teacher name. For development, if MAIL_SUPPRESS_SEND is True, print email to console.
> - Teacher dashboard should show their own leave requests with status.
> - Add models relationships for leave requests.

### Step 9: Academic Calendar with Teacher Notes
**Prompt:**
> Integrate FullCalendar.js in the base template or specific pages. Create routes:
> - `/academic-calendar` (accessible to all roles): displays calendar with notes.
> - For teachers: allow adding/editing/deleting their own notes on specific dates (click on date to open modal). Form fields: date, title, description, is_public (checkbox). Save to AcademicCalendarNotes.
> - For admin: see all notes, with ability to delete any note.
> - For students: view only public notes.
> Use JSON endpoints to fetch notes and handle CRUD via AJAX.

### Step 10: Syllabus Progress Tracking
**Prompt:**
> Add a teacher page `/teacher/syllabus-progress` that lists all courses assigned to that teacher (from timetable entries). For each course, show a slider or input to enter percentage covered (0-100). Save/update in SyllabusProgress table. On teacher dashboard, show average progress across courses.

### Step 11: Analytics Dashboards
**Prompt:**
> Create analytics dashboards:
> - Teacher dashboard: show total assigned lectures (count from timetable_entries), total leaves taken (approved), total leaves pending, average syllabus coverage, and a bar chart (using Chart.js) of lectures per week. Also show substitution assignments received.
> - Admin dashboard: show overall stats: total faculty, total students, total courses, total rooms. A table listing each teacher with lectures assigned, leaves approved, syllabus coverage %, substitutions done. Include a bar chart of leaves per teacher and a pie chart of syllabus coverage distribution (0-25%, 25-50%, 50-75%, 75-100%). Use Chart.js.

### Step 12: Metallic UI Polish & Animations
**Prompt:**
> Enhance all templates with the metallic chic design described in Section 5. Apply glassmorphism cards, metal buttons, gradient backgrounds, and smooth animations. Use AOS library for scroll animations (include via CDN). Add Font Awesome icons to buttons and nav items. Ensure mobile responsiveness with Bootstrap grid. Add a custom style.css with variables for colors and reusable classes.

### Step 13: Final Integration & Testing
**Prompt:**
> Review all modules for integration issues. Ensure the app can be run with `flask run`. Add a seed script (optional) to populate dummy data for testing. Fix any bugs found. Provide instructions for setting up Gmail SMTP with app password. Ensure password hashing works, email sending works (or console fallback), and all routes are protected by role. Generate requirements.txt final version.

## 7. Timetable Generation Algorithm Explained

```
Input:
- Courses list with type, hours_per_week, section, elective_basket
- Sections
- Faculty list with max_hours constraints
- Rooms with type
- Time slots (days x periods)

Steps:
1. Create empty schedule grid: dictionary mapping (time_slot_id) -> list of entries.
2. Prepare list of all required course assignments. Each course needs `hours_per_week` slots, but for simplicity, one slot per week per course (or divide).
3. Sort assignments by difficulty: labs first, electives, then theory.
4. For electives: group courses in same elective_basket for a section. Assign all electives in that basket to the same time slot (parallel). Find a time slot where all required rooms are available and faculty are free.
5. For other courses: use backtracking:
   - Recursively assign a course to a time slot that satisfies all hard constraints.
   - If no slot found, backtrack to previous assignment and try another.
6. Continue until all assigned or no solution.
7. Return entries list.
```

## 8. Email Setup (Gmail)

1. Enable 2-Step Verification on Gmail.
2. Generate an App Password: Google Account → Security → App passwords.
3. In `config.py`:
```python
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'your_email@gmail.com'
MAIL_PASSWORD = 'your_app_password'
MAIL_DEFAULT_SENDER = 'your_email@gmail.com'
```
4. For development, set `MAIL_SUPPRESS_SEND = True` and `MAIL_DEBUG = True` to print emails to console.

## 9. Running the Application

```bash
pip install -r requirements.txt
flask run
```

Visit `http://127.0.0.1:5000`. Create an admin user manually via shell or a seed script.

## 10. Additional Tips

- Use Git for version control; commit after each module.
- Keep prompts small and focused to get best results from AI.
- Test every module immediately.
- Focus on core timetable generation first; other features can be added later.
- For hackathon demo, pre-populate with sample data to showcase features.

---
```