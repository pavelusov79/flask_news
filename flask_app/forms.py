from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, EmailField, TextAreaField)
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp


class LoginForm(FlaskForm):
    username = StringField('Ваш логин', validators=[DataRequired()])
    password = PasswordField('Пароль',  validators=[DataRequired()])


class RegisterForm(FlaskForm):
    username = StringField('Ваш логин', validators=[DataRequired()])
    password1 = PasswordField('Пароль',  validators=[DataRequired(), Length(min=8, message="Длина пароля минимум 8 символов"), 
                              Regexp(r'^[0-9,a-z]*[a-z,_]*[A-Z][A-Z,a-z,_,0-9]*$', message="Пароль должен состоять из заглавных\
                              и строчных букв латиницы. Также может содержать цифры и знак '_'. Другие знаки не допустимы. \
                              Длина пароля минимум 8 символов")]
                              )
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password1', message='Пароли не совпадают. Повторите ввод.')])
    name = StringField('Ваше имя', validators=[DataRequired(), Length(min=3, max=12)])
    email = EmailField('Ваш email', validators=[DataRequired(), Email(message="Ваш email некорректен. Проверьте правильность написания")])


class CommentForm(FlaskForm):
    text = TextAreaField('Ваш комментарий', validators=[DataRequired(), Length(max=512, message="Допускается не более 512 символов. Сократите ваш комментарий.")])
