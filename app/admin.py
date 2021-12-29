from flask_admin.contrib.sqla import ModelView
from app import db
from .models import User


def add_admin_views():
    """Register admin views"""

    class UserModelView(ModelView):

        column_list = ['email', 'name', 'role_id', 'member_since',
                       'is_administrator']

    from . import app_admin
    app_admin.add_view(UserModelView(User, db.session, name='Users'))
