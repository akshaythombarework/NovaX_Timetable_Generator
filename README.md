# NovaX Timetable Generator

A web-based academic timetable management and generation system built with **Python and Flask**. NovaX is designed to help educational institutions manage academic schedules, faculty, courses, rooms, sections, leaves, academic calendars, and syllabus progress through role-based dashboards.

The system also includes a **constraint-based timetable generation engine** that uses backtracking and heuristics to create schedules while considering available academic resources and scheduling constraints.

## 🚀 Features

### 🔐 Role-Based Authentication

* Secure user login using username or email
* Password hashing with Werkzeug
* Role-based access control
* Separate dashboards for:

  * Administrator
  * Teacher
  * Student

### 👨‍💼 Admin Dashboard

Administrators can manage and monitor the academic scheduling environment, including:

* Departments
* Faculty members
* Courses
* Rooms
* Student sections
* Elective baskets
* Time slots
* Timetable entries
* Institution settings
* Faculty leave requests
* Academic calendar
* Analytics and reports

### 🧑‍🏫 Teacher Dashboard

Teachers can:

* View their timetable
* Monitor teaching schedules
* Apply for leave
* Select/request substitute faculty
* Track syllabus progress
* Update topics covered
* View relevant academic information

### 🎓 Student Dashboard

Students can:

* View their academic timetable
* Select their section
* View today's lectures
* See the next upcoming class
* Access academic calendar announcements
* View their complete weekly schedule

### 🧠 Intelligent Timetable Generation

NovaX includes a timetable generation engine based on **constraint satisfaction, backtracking, and heuristics**.

The generator works with resources such as:

* Courses
* Faculty
* Rooms
* Sections
* Time slots
* Departments
* Semesters
* Elective baskets

The generation engine tracks scheduling metrics such as assigned slots, required slots, clashes, and constraint violations.

### 📅 Academic Calendar

The system provides academic calendar management with support for:

* Academic events
* Public announcements
* Calendar notes
* Date-based academic information

### 📝 Leave Management

Teachers can submit leave requests with:

* Start date
* End date
* Reason
* Suggested substitute faculty

Administrators can approve or reject requests and assign substitute faculty when required.

### 📊 Analytics & Reports

The admin system includes analytics for areas such as:

* Faculty teaching loads
* Syllabus coverage
* Progress distribution
* Academic scheduling information

### 🔌 API Support

NovaX includes API routes for application data such as academic calendar events and timetable-related functionality.

---

## 🛠️ Technology Stack

| Technology       | Purpose                        |
| ---------------- | ------------------------------ |
| Python           | Backend programming            |
| Flask            | Web application framework      |
| Flask-SQLAlchemy | Database ORM                   |
| Flask-Login      | Authentication and sessions    |
| Flask-Mail       | Email functionality            |
| SQLite           | Development database           |
| Werkzeug         | Password hashing and utilities |
| HTML/CSS         | Frontend                       |
| Jinja2           | Server-side templates          |

---

## 📁 Project Structure

```text
NovaX_Timetable_Generator/
│
├── generator/
│   ├── __init__.py
│   └── algorithm.py
│
├── routes/
│   ├── __init__.py
│   ├── admin.py
│   ├── api.py
│   ├── auth.py
│   ├── student.py
│   └── teacher.py
│
├── static/
│   └── uploads/
│
├── templates/
│   ├── admin/
│   ├── errors/
│   ├── student/
│   ├── teacher/
│   ├── base.html
│   └── login.html
│
├── app.py
├── config.py
├── models.py
├── seed.py
├── test_routes.py
├── requirements.txt
├── database.db
├── LICENSE
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/akshaythombarework/NovaX_Timetable_Generator.git
```

### 2. Navigate to the project

```bash
cd NovaX_Timetable_Generator
```

### 3. Create a virtual environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Application

Start the Flask application with:

```bash
python app.py
```

The application runs locally on:

```text
http://127.0.0.1:5000
```

Open the URL in your browser.

---

## 🗄️ Database

NovaX uses **SQLite** for local development through Flask-SQLAlchemy.

The application automatically initializes the database tables when the application is started.

The database configuration can also be supplied through the `DATABASE_URL` environment variable.

---

## 🔑 Environment Configuration

For development, configuration values can be supplied using environment variables.

Recommended variables include:

```text
SECRET_KEY
DATABASE_URL
MAIL_SERVER
MAIL_PORT
MAIL_USE_TLS
MAIL_USERNAME
MAIL_PASSWORD
MAIL_DEFAULT_SENDER
```

Do not commit real credentials, passwords, API keys, or other secrets to the repository.

---

## 🧪 Testing

The project includes a route testing file:

```bash
python -m pytest
```

Or run the test file directly:

```bash
python test_routes.py
```

---

## 🧠 Timetable Generation

The timetable generator is implemented in:

```text
generator/algorithm.py
```

The generation engine uses a constraint-based approach with backtracking and heuristics.

The generator can work with:

* Departments
* Semesters
* Courses
* Sections
* Faculty
* Rooms
* Time slots
* Elective groups

The system also maintains generation metrics such as:

```text
Total slots required
Total slots assigned
Scheduling clashes
Constraint violations
```

This allows generated schedules to be evaluated and improved based on scheduling constraints.

---

## 🔒 Security

NovaX includes:

* Password hashing
* Login authentication
* Role-based authorization
* Protected admin routes
* Protected teacher routes
* Protected student routes
* Environment-based configuration support

For production deployment, replace development configuration values with secure environment variables and use a production-ready database and deployment configuration.

---

## 📌 Current Status

NovaX Timetable Generator is currently structured as a Flask-based academic scheduling application with:

* Role-based dashboards
* Database-backed academic management
* Timetable generation
* Faculty leave management
* Academic calendar
* Syllabus progress tracking
* Analytics
* API endpoints

The project is intended for further development and customization according to institutional scheduling requirements.

---

## 🔮 Future Improvements

Potential improvements include:

* Production deployment
* PostgreSQL/MySQL support
* Advanced timetable optimization
* More configurable scheduling constraints
* Automated conflict resolution
* PDF timetable export
* Excel timetable export
* Calendar synchronization
* Email notification integration
* Improved analytics dashboards
* Automated testing and CI/CD
* Responsive mobile interface

---

## 📄 License

This project is licensed under the **MIT License**.

See the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Akshay Thombare**

GitHub: [@akshaythombarework](https://github.com/akshaythombarework)

Project Repository: [NovaX_Timetable_Generator](https://github.com/akshaythombarework/NovaX_Timetable_Generator)

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.

Contributions, suggestions, and improvements are welcome.
