from flask import render_template, request, redirect, url_for
from tournament import app, login_manager, flask_login, r
from passlib.hash import pbkdf2_sha256
import re

@app.route('/')
def main():
  return render_template('main.html', user = flask_login.current_user)
 
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if not email:
        return

    email = email.lower()
    id = r.zscore('users', email)

    if not id:
        return
    user = User.get(id)
    user.is_authenticated = user.hash == request.form['pw']
    return user

@app.route('/register', methods=['GET'])
@app.route('/register/<error>', methods=['GET'])
def register(error = None):
    return render_template('register.html', errormessage=error)

@app.route('/register', methods=['POST'])
def create_user():
    email = request.form['email'].lower()
    if not isValidEmail(email):
        return redirect(url_for('register', error='Not a valid Email Address'))
    
    user_id = r.zscore('users', email)
    if user_id:
        return redirect(url_for('register', error='Email already registered'))
    
    user_id = int(r.incr('next_user_id'))
    nickname = request.form['nickname']
    hash = pbkdf2_sha256.encrypt(request.form['password'], rounds=200000, salt_size=16)
    
    user = User(user_id, email, nickname, hash)
    r.hmset('user:%s' % user.id, {'email': user.email, 'nickname': user.nickname, 'hash':user.hash})
    r.zadd('users',  user.email, user.id)
  
    flask_login.login_user(user)
    return redirect(url_for('main'))    

@app.route('/login', methods=['GET'])
@app.route('/login/<error>', methods=['GET'])
def login(error = None):
    return render_template('login.html', errormessage=error)

@app.route('/login', methods=['POST'])
def check_login():
    email = request.form['email'].lower()
    id = r.zscore('users', email)
    if id:
        user = User.get(id)
        if pbkdf2_sha256.verify(request.form['password'], user.hash):
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

def isValidEmail(email):
 if len(email) > 7:
    if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email) != None:
        return True
 return False
