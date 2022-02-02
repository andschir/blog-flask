from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('Имя пользователя', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[А-Яа-яA-Za-z][А-Яа-яA-Za-z0-9_.]*$', 0,
               'Имя пользователя должно содержать только буквы, цифры, точки или нижние подчеркивания')])
    password = PasswordField('Пароль', validators=[
        DataRequired(), EqualTo('password2', message='Пароли должны совпадать')])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Почтовый адрес уже зарегистрирован')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Пользователь с таки именем уже существует')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Старый пароль', validators=[DataRequired()])
    password = PasswordField('Новый пароль', validators=[
        DataRequired(), EqualTo('password2', message='Пароли должны совпадать')])
    password2 = PasswordField('Повторите новый пароль',
                              validators=[DataRequired()])
    submit = SubmitField('Обновить пароль')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Сбросить пароль')


class PasswordResetForm(FlaskForm):
    password = PasswordField('Новый пароль', validators=[
        DataRequired(), EqualTo('password2', message='Пароли должны совпадать')])
    password2 = PasswordField('Повторите новый пароль', validators=[DataRequired()])
    submit = SubmitField('Сбросить пароль')


class ChangeEmailForm(FlaskForm):
    email = StringField('Новый почтовый адрес', validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Обновить почтовый адрес')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Почтовый адрес уже зарегистрирован')
