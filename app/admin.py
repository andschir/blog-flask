import inspect

from flask import url_for
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose, Admin
from flask_admin.menu import MenuLink
from flask_login import current_user
from app import db
from .models import Permission, Role, User


class IndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not (current_user.is_authenticated and current_user.is_administrator):
            return self.render('403.html')
        return self.render('/admin/index.html')


app_admin = Admin(index_view=IndexView(name='Admin Dashboard'))


def add_admin_views():
    """Register admin views"""

    class RoleModelView(ModelView):
        list_template = 'admin/role.html'
        column_list = ['name', 'permissions']

        def render(self, template, **kwargs):
            if template == 'admin/role.html':
                kwargs['perms'] = Permission.get_attr(Permission)
            return super(RoleModelView, self).render(template, **kwargs)

    class UserModelView(ModelView):
        column_list = ['email', 'username', 'role.name', 'member_since']

    app_admin.add_view(RoleModelView(Role, db.session, name='Roles'))
    app_admin.add_view(UserModelView(User, db.session, name='Users'))
    app_admin.add_link(MenuLink(name='Exit Dashboard', url='/'))
