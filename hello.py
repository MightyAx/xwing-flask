from flask import Flask
from flask import render_template, request, redirect, url_for
app = Flask(__name__)

@app.route('/')
@app.route('/<username>')
def hello(username='World'):
#To-do:get list of greetings from database
  return render_template('hello.html', name=username)

@app.route('/shoutout', methods=['POST'])
def post_greeting():
#To-do: Save to database.
  return redirect(url_for('hello', username=request.form['name']))