from flask import Flask
from flask import render_template, request, redirect, url_for
import os, redis, datetime, flask_login

app = Flask(__name__)
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
    id = ""
    nickname = ""
    email = ""

@login_manager.user_loader
def user_loader(id):
    if not r.exists('user:%s' % id)
        return
    
    user = User()
    user.id = id
    user.nickname = r.hget('user:%s' % id, 'nickname').decode("utf-8")
    user.email = r.hget('user:%s' % id, 'email').decode("utf-8")
	user.hash = r.hget('user:%s' % id, 'hash')
	return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
	if not r.exists('email:%s' % email)
		return
	
	id = r.get('email:%s' % email)
	user = user_loader(id)
	
	#user.is_authenticated = hash(request.form['pw']) == user.hash
	return user
	