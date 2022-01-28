from flask_wtf import FlaskForm
# from flask_ckeditor import CKEditorField
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User, Post, Tag


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


from wtforms import TextAreaField
from wtforms.widgets import TextArea


class CKEditor(TextArea):
    def __call__(self, field, **kwargs):
        c = kwargs.pop('class', '') or kwargs.pop('class_', '')
        kwargs['class'] = u'%s %s' % ('ckeditor', c)
        return super(CKEditor, self).__call__(field, **kwargs)


class CKEditorField(TextAreaField):
    widget = CKEditor()


class TagField(StringField):
    def _value(self):
        if self.data:
            # Display tags as a comma-separated list.
            return ', '.join([tag.name for tag in self.data])
        return ''

    def get_tags_from_string(self, tag_string):
        raw_tags = tag_string.split(',')
        # Filter out any empty tag names.
        tag_names = [name.strip() for name in raw_tags if name.strip()]
        # Query the database and retrieve any tags we have already saved.
        existing_tags = Tag.query.filter(Tag.name.in_(tag_names))
        # Determine which tag names are new.
        new_names = set(tag_names) - set([tag.name for tag in existing_tags])
        # Create a list of unsaved Tag instances for the new tags.
        new_tags = [Tag(name=name) for name in new_names]
        # Return all the existing tags + all the new, unsaved tags.
        return list(existing_tags) + new_tags

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = self.get_tags_from_string(valuelist[0])
        else:
            self.data = []


class PostForm(FlaskForm):
    title = CKEditorField('Заголовок')
    body = TextAreaField('Текст')
    submit = SubmitField('Создать')
    status = SelectField(
        name='Опубликовать:',
        choices=(
            (Post.STATUS_DRAFT, 'как черновик'),
            (Post.STATUS_PUBLIC, 'публично')
        ),
        coerce=int
    )
    tags = TagField('Теги:',
                    render_kw={"placeholder": "Введите теги, разделяя их запятой",
                                        })


class CommentForm(FlaskForm):
    body = StringField('Введите ваш комментарий', validators=[DataRequired()])
    submit = SubmitField('Отправить')
