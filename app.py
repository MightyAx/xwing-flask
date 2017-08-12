from flask import Flask
from flask import render_template, request, redirect, url_for
from passlib.hash import pbkdf2_sha256 
import os, redis, datetime, flask_login, re

app = Flask(__name__)
app.secret_key = os.environ.get("SECURE_KEY")
r = redis.from_url(os.environ.get("REDIS_URL"))
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

@app.route('/')
def main():
  return render_template('main.html', user = flask_login.current_user)

@app.route('/feedback', methods=['GET'])
@app.route('/feedback/<username>', methods=['GET'])
def feedback(username='World'):
  keys = r.lrange('greetings', 0, -1)
  messages = []
  for key in keys:
    messages.append(dict(name = r.hget(key, 'name'), message = r.hget(key, 'message')))
  return render_template('feedback.html', name = username, messages = messages)

@app.route('/feedback', methods=['POST'])
def post_feedback():
  greeting_id = r.incr('next_greeting_id')
  r.hmset('greeting:%s' % greeting_id, {'name':request.form['name'], 'message':request.form['message'], 'timestamp':datetime.datetime.now()})
  r.lpush('greetings', 'greeting:%s' % greeting_id)
  return redirect(url_for('feedback', username=request.form['name']))

class User(flask_login.UserMixin):
    def __init__(self, id, email, nickname, hash):
        self.id = int(id)
        self.email = email.lower()
        self.nickname = nickname
        self.hash = hash

    @classmethod
    def get(cls, id):
        id = int(id)
        return cls(id, r.hget('user:%s' % id, 'email'), r.hget('user:%s' % id, 'nickname'), r.hget('user:%s' % id, 'hash'))
        
def isValidEmail(email):
 if len(email) > 7:
    if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email) != None:
        return True
 return False
 
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
