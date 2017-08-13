import flask_login
import os
import redis

from flask import Flask

app = Flask(__name__)
app.secret_key = os.environ.get("SECURE_KEY")
r = redis.from_url(os.environ.get("REDIS_URL"))
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# noinspection PyPep8
import tournament.models, tournament.views_main
