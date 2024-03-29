from flask import Markup, url_for

from flask_admin import AdminIndexView, Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from .fileadmin import FileAdmin
from flask_admin.model import typefmt
from datetime import date

from flask_login import current_user

from wtforms.fields import PasswordField, SelectField

from app import db
from .models import Permission, Role, User, Post, Tag, Comment

import warnings


class RestrictedAccess(object):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_administrator


class IndexView(RestrictedAccess, AdminIndexView):
    def is_visible(self):
        return False


app_admin = Admin(name='Панель Администратора', index_view=IndexView())



def add_admin_views(app_instance):
    """Register admin views"""

    def date_format(view, value):
        return value.strftime('%d %B %Y, %H:%M:%S')

    MY_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
    MY_DEFAULT_FORMATTERS.update({
        type(None): typefmt.null_formatter,
        date: date_format
    })

    class RoleModelView(RestrictedAccess, ModelView):
        def render(self, template, **kwargs):
            if template == 'admin/role.html':
                kwargs['perms'] = Permission.get_attr(Permission)
            return super(RoleModelView, self).render(template, **kwargs)
        # Adds information about permissions
        list_template = 'admin/role.html'
        column_list = ['name', 'permissions']
        column_labels = {
            'name': 'Название роли',
            'permissions': 'Разрешения',
        }
        action_disallowed_list = ['delete']

    class UserModelView(RestrictedAccess, ModelView):
        def on_model_change(self, form, model, is_created):
            if form.new_password.data:
                model.password = form.new_password.data
            return super(UserModelView, self).on_model_change(
                form, model, is_created)

        def _username_formatter(view, context, model, name):
            if name == 'username':
                profile_url = url_for('main.user', username=model.username)
                html = '''<p>{username}</p>
                <a href="{url}">
                    <span class="label label-default">Открыть профиль</span>
                </a>                
                '''.format(username=model.username, url=profile_url)

                return Markup(html)

        column_type_formatters = MY_DEFAULT_FORMATTERS

        column_list = [
            'email', 'username', 'role.name', 'member_since'
        ]
        column_formatters = {
            'username': _username_formatter,
        }
        column_labels = {
            'posts': 'Записи',
            'comments': 'Комментарии',
            'confirmed': 'Подтвержден',
            'role': 'Роль',
            'location': 'Локация',
            'about_me': 'О себе',
            'avatar_hash': 'Хеш аватара',
            'email': 'E-mail',
            'name': 'Имя',
            'username': 'Никнейм',
            'role.name': 'Роль',
            'member_since': 'Дата регистрации',
            'last_seen': 'Последний раз заходил'
        }
        column_filters = (
            'email', 'username', 'role.name', 'member_since'
        )
        column_searchable_list = (
            'email', 'username'
        )
        column_sortable_list = (
            'email', 'username', 'role.name', 'member_since'
        )
        column_default_sort = 'role.name'

        form_extra_fields = {
            'new_password': PasswordField('Новый пароль'),
        }
        form_edit_rules = [
            'posts', 'comments', 'email', 'username', 'new_password',
            'name', 'confirmed', 'role', 'location', 'about_me',
            'member_since', 'last_seen', 'avatar_hash',
        ]

        form_widget_args = {
            'password_hash': {
                'disabled': True
            },
            'member_since': {
                'disabled': True
            },
            'last_seen': {
                'disabled': True
            },
            'avatar_hash': {
                'disabled': True
            }
        }

    class PostModelView(RestrictedAccess, ModelView):
        def _id_formatter(view, context, model, name):
            if name == 'id':
                edit_url = url_for('main.post', id=model.id)
                html = '''<p>{id}</p>
                <a href="{url}">
                    <span class="label label-default">Открыть запись</span>
                </a>
                '''.format(id=model.id, url=edit_url)

                return Markup(html)

        def _html_formatter(view, context, model, name):
            if name == 'title':
                return Markup(model.title)
            if name == 'body':
                return Markup(model.body)[:200]

        _status_choices = [(choice, label) for choice, label in [
            (Post.STATUS_PUBLIC, 'Опубликовано'),
            (Post.STATUS_DRAFT, 'Черновик'),
            (Post.STATUS_DELETED, 'Удалено'),
            (Post.STATUS_HIDDEN, 'Скрыто'),
            (Post.STATUS_POSTPONED, 'Отложено'),
        ]]
        # Restricts col's height by 8em
        list_template = 'admin/post.html'

        column_choices = {
            'status': _status_choices,
        }
        can_create = False

        column_type_formatters = MY_DEFAULT_FORMATTERS

        column_list = [
            'id', 'status', 'timestamp', 'timestamp_modified', 'author.username', 'title', 'body'
        ]
        column_filters = (
            'id', 'status', 'timestamp', 'timestamp_modified', 'author.username', 'title', 'body'
        )
        column_searchable_list = (
            'title', 'body'
        )
        column_sortable_list = (
            'id', 'status', 'timestamp', 'timestamp_modified', 'author.username', 'title', 'body'
        )
        column_default_sort = ('id', True)
        column_labels = {
            'id': 'Порядковый номер',
            'status': 'Статус',
            'timestamp': 'Дата создания',
            'timestamp_modified': 'Дата изменения',
            'author.username': 'Автор',
            'title': 'Заголовок',
            'body': 'Текст',
            'comments': 'Комментарии',
            'tags': 'Теги',
            'author': 'Автор',
            'publish_date': 'Дата отложенной публикации',
        }
        column_formatters = {
            'id': _id_formatter,
            'title': _html_formatter,
            'body': _html_formatter
        }
        form_columns = [
            'comments', 'tags', 'status', 'timestamp', 'timestamp_modified', 'publish_date', 'author'
        ]
        form_overrides = {'status': SelectField}
        form_args = {
            'status': {
                'choices': _status_choices,
                'coerce': int
            }
        }
        form_widget_args = {
            'timestamp': {
                'disabled': True
            },
            'timestamp_modified': {
                'disabled': True
            },
            'publish_date': {
                'disabled': True
            }
        }
        form_ajax_refs = {
            'author': {
                'fields': (User.username, User.email),
                'page-size': 10,
            },
        }

    class TagModelView(RestrictedAccess, ModelView):
        def render(self, template, **kwargs):
            if template == 'admin/tag.html':
                kwargs['tags'] = Tag.query.all()
            return super(TagModelView, self).render(template, **kwargs)
        # Adds notification for tags with no posts associated
        list_template = 'admin/tag.html'
        column_list = ['id', 'name', 'tags_count']
        column_labels = {
            'id': 'Порядковый номер',
            'name': 'Название тега',
            'tags_count': 'Количество записей с этим тегом',
            'slug': 'Slug',
            'posts': 'Связанные записи'
        }
        column_sortable_list = (
            'id', 'name', 'tags_count'
        )
        column_filters = [
            'name'
        ]
        column_searchable_list = [
            'name'
        ]
        form_columns = [
            'name', 'slug', 'posts'
        ]
        form_widget_args = {
            'slug': {
                'disabled': True
            },
        }


        def on_model_change(self, form, model, is_created):
            model.generate_slug()

    class CommentModelView(RestrictedAccess, ModelView):
        def _post_id_formatter(view, context, model, name):
            if name == 'post_id':
                    edit_url = url_for('main.post', id=model.post_id)
                    html = '''<p>{post_id}</p>
                    <a href="{url}">
                        <span class="label label-default">Открыть запись</span>                        
                    </a>
                    '''.format(post_id=model.post_id, url=edit_url)

                    return Markup(html)

        _status_choices = [(choice, label) for choice, label in [
            (Comment.STATUS_PUBLIC, 'Опубликовано'),
            (Comment.STATUS_DELETED_BY_USER, 'Удалено пользователем'),
            (Comment.STATUS_DISABLED_BY_MODERATOR, 'Удалено модератором'),
        ]]

        column_type_formatters = MY_DEFAULT_FORMATTERS
        can_create = False
        column_list = ['id', 'author.username', 'post_id', 'body', 'timestamp', 'status']
        column_labels = {
            'id': 'Порядковый номер',
            'author.username': 'Автор',
            'post_id': 'Номер связанной записи',
            'body': 'Текст',
            'timestamp': 'Дата создания',
            'status': 'Статус',
            'author': 'Автор',
            'post': 'Связанная запись'
        }
        column_choices = {
            'status': _status_choices,
        }
        column_sortable_list = (
            'id', 'author.username', 'post_id', 'timestamp', 'status'
        )
        column_filters = [
            'author.username', 'post_id', 'body', 'timestamp', 'status'
        ]
        column_searchable_list = [
            'author.username', 'post_id',
        ]
        column_formatters = {
            'post_id': _post_id_formatter,
        }
        form_columns = [
            'body', 'status', 'timestamp', 'author', 'post'
        ]
        form_overrides = {'status': SelectField}
        form_args = {
            'status': {
                'choices': _status_choices,
                'coerce': int
            }
        }
        form_widget_args = {
            'timestamp': {
                'disabled': True
            },
        }
        form_ajax_refs = {
            'author': {
                'fields': (User.username, User.email),
                'page-size': 10,
            },
        }

    class StaticFileAdmin(RestrictedAccess, FileAdmin):
        def is_accessible(self):
            return current_user.is_authenticated and current_user.is_administrator

    class UploadFileAdmin(RestrictedAccess, FileAdmin):
        pass

    app_admin.add_view(RoleModelView(Role, db.session, name='Роли'))
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', 'Fields missing from ruleset', UserWarning)
        app_admin.add_view(UserModelView(User, db.session, name='Пользователи'))
    app_admin.add_view(PostModelView(Post, db.session, name='Записи'))
    app_admin.add_view(TagModelView(Tag, db.session, name='Теги'))
    app_admin.add_view(CommentModelView(Comment, db.session, name='Комментарии'))
    app_admin.add_view(StaticFileAdmin(
        app_instance.config['STATIC_DIR'], '/static/', name='Cтатические файлы'))
    app_admin.add_view(UploadFileAdmin(
        app_instance.config['UPLOADS_DIR'], name='Загруженные файлы'))

    app_admin.add_link(MenuLink(name='APScheduler Jobs', url='/scheduler/jobs'))
    app_admin.add_link(MenuLink(name='Выход', url='/'))
