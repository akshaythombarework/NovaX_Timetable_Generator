import sys
import requests

BASE_URL = 'http://127.0.0.1:5000'
session = requests.Session()

def test_endpoint(path, expected_status=200, method='GET', data=None):
    url = BASE_URL + path
    try:
        if method == 'GET':
            resp = session.get(url, allow_redirects=True)
        else:
            resp = session.post(url, data=data, allow_redirects=True)
        
        status = resp.status_code
        is_ok = (status == expected_status)
        print(f"[{'PASS' if is_ok else 'FAIL'}] {method} {path} -> {status}")
        return is_ok
    except Exception as e:
        print(f"[FAIL] {method} {path} -> Exception: {e}")
        return False

print("--- Testing NovaX HTTP Endpoints ---")
# 1. Login Page
test_endpoint('/login')

# 2. Demo Login as Admin
test_endpoint('/demo-login/admin')

# 3. Admin Routes
test_endpoint('/admin/dashboard')
test_endpoint('/admin/timetable')
test_endpoint('/admin/backup-plan')
test_endpoint('/admin/faculty')
test_endpoint('/admin/courses')
test_endpoint('/admin/rooms')
test_endpoint('/admin/sections')
test_endpoint('/admin/elective-baskets')
test_endpoint('/admin/time-slots')
test_endpoint('/admin/leaves')
test_endpoint('/admin/academic-calendar')
test_endpoint('/admin/analytics')
test_endpoint('/admin/settings')

# 4. Demo Login as Teacher
test_endpoint('/demo-login/teacher')
test_endpoint('/teacher/dashboard')
test_endpoint('/teacher/timetable')
test_endpoint('/teacher/apply-leave')
test_endpoint('/teacher/syllabus-progress')
test_endpoint('/teacher/academic-calendar')

# 5. Demo Login as Student
test_endpoint('/demo-login/student')
test_endpoint('/student/dashboard')
test_endpoint('/student/timetable')
test_endpoint('/student/academic-calendar')

# 6. API Endpoints
test_endpoint('/api/calendar/events')

print("\n--- All Route Tests Completed ---")
