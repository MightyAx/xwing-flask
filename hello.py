from flask import Flask
from flask import render_template, request, redirect, url_for
app = Flask(__name__)

@app.route('/')
@app.route('/<username>')
def hello(username=None):
    return render_template('hello.html', name=username)

@app.route('/shoutout', methods=['POST'])
def shout_out():
  return redirect(url_for('hello', username=request.form['name']))