import os
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASKY_POSTS_PER_PAGE = 20
    FLASKY_FOLLOWERS_PER_PAGE = 50
    FLASKY_COMMENTS_PER_PAGE = 30

    STATIC_DIR = os.path.join(basedir, 'app/static')
    UPLOADS_DIR = os.path.join(basedir, 'uploads')

    MAX_CONTENT_LENGTH = 20 * 1024 * 1024
    UPLOADED_PATH_IMAGES = os.path.join(basedir, 'uploads/img/')

    SSL_REDIRECT = False

    SCHEDULER_API_ENABLED = True
    
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    SCHEDULER_JOBSTORES = {
        "default": SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)
    }


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'
    SCHEDULER_JOBSTORES = {
        "default": SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)
    }


class ProductionConfig(Config):
    # workaround for missing SQLAlchemy dialect: postgres:// > postgresql://
    database_path = os.environ.get('DATABASE_URL')
    if database_path and database_path.startswith('postgres://'):
        database_path = database_path.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = database_path or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SCHEDULER_JOBSTORES = {
        "default": SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)
    }

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.FLASKY_MAIL_SENDER,
            toaddrs=[cls.FLASKY_ADMIN],
            subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class HerokuConfig(ProductionConfig):
    SSL_REDIRECT = True if os.environ.get('DYNO') else False

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        # handle reverse proxy server headers
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,

    'default': DevelopmentConfig
}
