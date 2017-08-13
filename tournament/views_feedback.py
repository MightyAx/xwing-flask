from flask import render_template, request, redirect, url_for
from tournament import app, r
import datetime


@app.route('/feedback', methods=['GET'])
def feedback():
    keys = r.lrange('greetings', 0, -1)
    messages = []
    for key in keys:
        messages.append(dict(name=r.hget(key, 'name'), message=r.hget(key, 'message')))
    return render_template('feedback.html', messages=messages)


@app.route('/feedback', methods=['POST'])
def post_feedback():
    greeting_id = r.incr('next_greeting_id')
    r.hmset('greeting:%s' % greeting_id,
            {'name': request.form['name'], 'message': request.form['message'], 'timestamp': datetime.datetime.now()})
    r.lpush('greetings', 'greeting:%s' % greeting_id)
    return redirect(url_for('feedback'))
