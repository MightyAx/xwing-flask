from flask import render_template, request, redirect, url_for, flash

from tournament import app, login_manager, flask_login, r
from passlib.hash import pbkdf2_sha256
from tournament.models import User
from tournament.forms import Register, Login


@app.route('/')
def main():
    return render_template('main.html', user=flask_login.current_user)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = Register(request.form)
    if request.method == 'POST':
        if form.validate():
            user = User.create(form.email.data, form.name.data, form.password.data)

            flask_login.login_user(user)
            flash('Registration Successful')
            return redirect(url_for('main'))
        else:
            flash('Registration Failure')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = Login(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        user_id = User.exists(form.email.data)
        if user_id:
            user = User.get(user_id)
            if pbkdf2_sha256.verify(form.password.data, user.Hash):
                flask_login.login_user(user)
                flash('Login Successful')
                return redirect(url_for('main'))
        flash('Incorrect Email or Password')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('main'))


@login_manager.unauthorized_handler
def unauthorized_handler():
    flash('Unauthorized')
    return redirect(url_for('main'))
