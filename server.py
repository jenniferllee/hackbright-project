from jinja2 import StrictUndefined
from flask import (Flask, jsonify, render_template, redirect, request, flash,
                   session, url_for)
from flask_debugtoolbar import DebugToolbarExtension
from model import (User, Medication, Frequency, Compliance, Reminder,
                   connect_to_db, db)
from datetime import datetime

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Raises an error if you use an undefined variable in Jinja2
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def login():
    """Homepage with login."""

    return render_template("login.html")
