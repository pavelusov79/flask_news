from flask import Blueprint, render_template, url_for, redirect, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user

from .models import User
from .database import db_session
from .forms import LoginForm, RegisterForm


auth = Blueprint('auth', __name__)

@auth.route('/login/', methods = ['POST','GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and check_password_hash(user.password, form.password.data):
            login_user(user)
            next = request.args.get("next")
            if user.is_admin:
                return redirect(url_for('admin.index'))
            else:
                if next:
                    return redirect(next)
                if 'prev_page' in session:
                    return redirect(session['prev_page'])
            return redirect(url_for('main.index'))
        if user is None:
            flash('Пользователь с таким логином не найден в базе')
    return render_template('auth/login.html', form=form)


@auth.route('/singup/', methods = ['POST','GET'])
def singup():
    if 'prev_page' not in session:
        session['prev_page'] = request.referrer
    form = RegisterForm()
    if form.validate_on_submit():
        username = User.query.filter_by(username=form.username.data).first()
        if username:
            flash('Такой логин уже есть в базе. Выберите другой логин или пройдите авторизацию если вы регистрировались.')
        user_email = User.query.filter_by(email=form.email.data).first()
        if user_email:
            flash('Такой емэйл уже есть в базе данных. Выберите другой емэйл.')
        user = User(name=form.name.data, 
                    username=form.username.data,
                    email=form.email.data, 
                    password=generate_password_hash(form.password1.data))
        if not username and not user_email:
            db_session.add(user)
            db_session.commit()
            return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

    


