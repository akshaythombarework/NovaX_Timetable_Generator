import os
from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager, current_user
from flask_mail import Mail
from config import Config
from models import db, User, InstitutionSettings, LeaveRequest

mail = Mail()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes import auth_bp, admin_bp, teacher_bp, student_bp, api_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(api_bp)

    # Context processors
    @app.context_processor
    def inject_global_data():
        try:
            settings = InstitutionSettings.get_settings()
        except Exception:
            settings = None
            
        pending_leaves_count = 0
        if current_user.is_authenticated and current_user.role == 'admin':
            try:
                pending_leaves_count = LeaveRequest.query.filter_by(status='pending').count()
            except Exception:
                pending_leaves_count = 0

        return {
            'institution': settings,
            'pending_leaves_count': pending_leaves_count
        }

    # Template filters
    @app.template_filter('datetime_format')
    def datetime_format(value, format='%d %b %Y, %I:%M %p'):
        if value is None:
            return ""
        return value.strftime(format)

    @app.template_filter('date_format')
    def date_format(value, format='%d %b %Y'):
        if value is None:
            return ""
        return value.strftime(format)

    # Root route - Always show Login Page / Role Selector first
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    # Custom Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        # Ensure uploads folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='127.0.0.1', port=5000)
