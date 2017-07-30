from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route('/')
@app.route('/<username>')
def hello(username=None):
    return render_template('hello.html', name=username)