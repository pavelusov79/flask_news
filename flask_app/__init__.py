import os
import datetime
from flask import Flask
from flask_login import LoginManager, current_user
from flask_admin import Admin
from dotenv import load_dotenv
from flask_mail import Mail

from .database import db_session
from .models import User


load_dotenv()
mail = Mail()
admin = Admin(name='flask_app', base_template="admin/index.html", template_mode='bootstrap4')

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
    app.config['MAIL_DEFAULT_SENDER'] = os.environ['MAIL_USERNAME']
    app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
    app.config['ADMINS'] = os.environ['ADMINS']
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

    admin.init_app(app)
    mail.init_app(app)

    #blueprints
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .admin import admin_app as admin_blueprint
    app.register_blueprint(admin_blueprint)

    @app.context_processor
    def inject_now():
        return {'now': datetime.datetime.now()}
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    @app.teardown_appcontext
    def remove_session(exception=None):
        return db_session.remove()

    return app
    