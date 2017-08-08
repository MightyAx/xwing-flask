from flask import Flask
from flask import render_template, request, redirect, url_for
import os, redis, datetime, flask_login

app = Flask(__name__)
app.secret_key = os.environ.get("SECURE_KEYS")
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
    messages.append(dict(name = r.hget(key, 'name').decode("utf-8"), message = r.hget(key, 'message').decode("utf-8")))
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
        self.email = email.decode('utf-8')
        self.nickname = nickname.decode('utf-8'),
        self.hash = hash.decode('utf-8')

    @classmethod
    def get(cls, id):
        id = int(id)
        return cls(id, r.hget('user:%s' % id, 'email'), r.hget('user:%s' % id, 'nickname'), r.hget('user:%s' % id, 'hash'))
        
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    id = r.zscore('users', email)
    if not id:
        return
    user = User.get(id)
    user.is_authenticated = user.hash == request.form['pw']
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    email = request.form['email']
    id = r.zscore('users', email)
    if id:
        user = User.get(id)
        if user and user.hash == request.form['password']:
            flask_login.login_user(user)
            return redirect(url_for('main'))
    return render_template('login.html', errormessage='Incorrect Email or Password')

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('main')) 

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('login.html', errormessage='Unauthorized')
