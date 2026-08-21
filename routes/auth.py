from functools import wraps
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Faculty
from . import auth_bp

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))
            if current_user.role not in roles:
                flash(f"Access denied. You do not have permissions for this page.", "danger")
                if current_user.role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif current_user.role == 'teacher':
                    return redirect(url_for('teacher.dashboard'))
                else:
                    return redirect(url_for('student.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')
        selected_role = request.form.get('role', '')

        user = User.query.filter(
            (User.username == login_input) | (User.email == login_input)
        ).first()

        if user and user.check_password(password):
            if selected_role and user.role != selected_role:
                flash(f"Account found, but role does not match '{selected_role}'. Logged in as {user.role.capitalize()}.", "warning")
            
            login_user(user, remember=True)
            flash(f"Welcome back, {user.username}!", "success")
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
                
            if user.role == 'admin':
                return redirect(url_for('admin.timetable'))
            elif user.role == 'teacher':
                return redirect(url_for('teacher.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
        else:
            flash("Invalid email/username or password. Please try again.", "danger")

    return render_template('login.html')

@auth_bp.route('/demo-login/<role>')
def demo_login(role):
    """Quick demo login route for instant switching between roles."""
    if role == 'admin':
        user = User.query.filter_by(role='admin').first()
    elif role == 'teacher':
        user = User.query.filter_by(role='teacher').first()
    elif role == 'student':
        user = User.query.filter_by(role='student').first()
    else:
        user = None

    if user:
        login_user(user, remember=True)
        flash(f"Logged in as {role.capitalize()} Portal: {user.username}", "info")
        if user.role == 'admin':
            return redirect(url_for('admin.timetable'))
        elif user.role == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))
    
    flash(f"Demo user for role '{role}' not found. Please run seed script.", "warning")
    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for('auth.login'))
