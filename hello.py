from flask import Flask
app = Flask(__name__)

@app.route("/")
def helloworld():
    return hello("World")
    
@app.route("/<username>")
def hello(username):
    return "Hello %s!" % username 