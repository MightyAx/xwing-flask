from flask import render_template, request, redirect, url_for, flash

from tournament import app, login_manager, flask_login, r
from passlib.hash import pbkdf2_sha256
from tournament.models import User
from tournament.forms import Register
import re


@app.route('/')
def main():
    return render_template('main.html', user=flask_login.current_user)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = Register()
    if form.validate_on_submit():
        user_id = int(r.incr('next_user_id'))
        pw_hash = pbkdf2_sha256.encrypt(form.password.data, rounds=200000, salt_size=16)

        user = User(user_id, form.email.data, form.name.data, pw_hash)
        r.hmset('user:%s' % user.UserId, {'email': user.Email, 'nickname': user.Nickname, 'hash': user.Hash})
        r.zadd('users', user.Email, user.UserId)

        flask_login.login_user(user)
        flash('Registration Sucessful')
        return redirect(url_for('main'))
    else:
        flash('Registration Failure')
    return render_template('register.html', form = form)


@app.route('/login', methods=['GET'])
@app.route('/login/<error>', methods=['GET'])
def login(error=None):
    return render_template('login.html', errormessage=error)


@app.route('/login', methods=['POST'])
def check_login():
    email = request.form['email'].lower()
    user_id = User.exists(email)
    if user_id:
        user = User.get(user_id)
        if pbkdf2_sha256.verify(request.form['password'], user.Hash):
            flask_login.login_user(user)
            return redirect(url_for('main'))
    return redirect(url_for('login', error='Incorrect Email or Password'))


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('main'))


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login', error='Unauthorized'))
