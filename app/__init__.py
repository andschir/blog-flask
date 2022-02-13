from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask_apscheduler import APScheduler
from config import config
import locale

bootstrap = Bootstrap5()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
ckeditor = CKEditor()
scheduler = APScheduler()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

app_language = 'ru_UA.utf8'
locale.setlocale(locale.LC_ALL, app_language)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    if app.config['SSL_REDIRECT']:
        from flask_sslify import SSLify
        sslify = SSLify(app)
    
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    ckeditor.init_app(app)
    scheduler.init_app(app)
    scheduler.start()
    from app.admin import app_admin
    app_admin.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from app.admin import add_admin_views
    add_admin_views(app)

    return app
