from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User, Post, Tag


class EditProfileForm(FlaskForm):
    name = StringField('Реальное имя', validators=[Length(0, 64)])
    location = StringField('Локация', validators=[Length(0, 64)])
    about_me = TextAreaField('Обо мне')
    submit = SubmitField('Подтвердить')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('Имя пользователя', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Имя пользователя должно содержать только буквы, цифры, точки или нижние подчеркивания')])
    confirmed = BooleanField('Подтвержден')
    role = SelectField('Роль', coerce=int)
    name = StringField('Реальное имя', validators=[Length(0, 64)])
    location = StringField('Локация', validators=[Length(0, 64)])
    about_me = TextAreaField('Обо мне')
    submit = SubmitField('Подтвердить')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Почтовый адрес уже зарегистрирован')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Пользователь с таки именем уже существует')


class TagField(StringField):
    def _value(self):
        if self.data:
            # Display tags as a comma-separated list.
            return ', '.join(sorted([tag.name for tag in self.data], reverse=True))
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
    title = TextAreaField('Заголовок')
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
                    render_kw={"placeholder": "Введите теги, разделяя их запятой"})


class CommentForm(FlaskForm):
    body = StringField('Введите ваш комментарий', validators=[DataRequired()])
    submit = SubmitField('Отправить')
