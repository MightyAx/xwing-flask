from flask import Flask
from flask import render_template, request, redirect, url_for
import os, redis, datetime, flask_login

app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!
r = redis.from_url(os.environ.get("REDIS_URL"))
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

@app.route('/')
def main():
  return render_template('main.html')

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
        self.email = email
        self.nickname = nickname,
        self.hash = hash

    @classmethod
    def get(cls, id):
        id = int(id)
        return cls(id, r.hget('user:%s' % id, 'email').decode('utf-8'), r.hget('user:%s' % id, 'nickname'), r.hget('user:%s' % id, 'hash').decode('utf-8'))
        
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    id = int(r.zscore('users', email))
    if not user.id:
        return
    user = User.get(id)
    user.is_authenticated = user.hash == request.form['pw']
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'></input>
                <input type='password' name='pw' id='pw' placeholder='password'></input>
                <input type='submit' name='submit'></input>
               </form>
               '''

    email = request.form['email']
    id = int(r.zscore('users', email))
    user = User.get(id)
    if user and user.hash == request.form['pw']:
        flask_login.login_user(user)
        return redirect(url_for('protected'))

    return 'Bad login: id: {}, email: {}, auth: {}, hash: {}, pw: {}'.format(flask_login.current_user.id, flask_login.current_user.email, flask_login.current_user.is_authenticated, r.hget('user:%s' % user.id, 'hash'), request.form['pw'])

@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.email

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'
    
#@login_manager.unauthorized_handler
#def unauthorized_handler():
#    return 'Unauthorized'
