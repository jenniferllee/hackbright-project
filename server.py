from jinja2 import StrictUndefined
from flask import (Flask, jsonify, render_template, redirect, request, flash,
                   session, url_for)
from flask_debugtoolbar import DebugToolbarExtension
from model import (User, Medication, Frequency, Compliance,
                   connect_to_db, db)
from datetime import datetime

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Raises an error if you use an undefined variable in Jinja2
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def homepage():
    """Homepage."""

    return render_template("homepage.html")


@app.route("/login")
def login():
    """Sign up for an account."""

    return render_template("login.html")


@app.route("/login-success", methods=["POST"])
def handle_login_form():
    """If user is already registered, user is logged in and taken to user page.
    If user is new, flash message asks user to sign up.
    """

    # Get email and password from login form.
    email = request.form.get("email")
    password = request.form.get("password")

    user = db.session.query(User).filter(User.email == email).first()

    # If user exists, check if password matches.
    if user:

        # If password is correct, login user to user page.
        if password == user.password:
            session['Logged in user'] = user.user_id
            flash("Welcome, " + user.fname + "! You are logged in.")
            return redirect(url_for('show_user_page',
                                    user_id=session['Logged in user']))

        # If password is incorrect, flash "Password invalid."
        else:
            flash("Password invalid.")
            return redirect("/login")

    # If user does not exist, ask user to register.
    else:
        flash("You are not registered. Please sign up for an account.")
        return redirect("/login")


@app.route("/register")
def register():
    """New user registration form."""

    return render_template("register.html")


@app.route("/register-success", methods=["POST"])
def handle_registration_info():
    """Handle registration submission and redirect to login page."""

    # Get name, email and password from registration form submission.
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    email = request.form.get("email")
    password = request.form.get("password")

    user = db.session.query(User).filter(User.email == email).first()

    # If user email already exists, redirect to login page.
    if user:
        flash("You are already registered. Please log in.")
        return redirect("/login")

    # Otherwise, add new user to database and redirect to login page.
    else:
        new_user = User(fname=fname, lname=lname, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account successfully created! Please log in.")
        return redirect("/login")


@app.route("/user/<user_id>")
def show_user_page(user_id):
    """Displays individual user page with medication list."""

    # Display medication name, dose, frequency, time
    meds = db.session.query(Medication.name, Medication.dose).filter((Frequency.user_id == user_id) & (Frequency.med_id == Medication.med_id)).all()

    return render_template("user.html", meds=meds)


@app.route("/logout")
def logout():
    """Logs user out and removes user ID from session."""

    del session['Logged in user']
    print session

    flash("You successfully logged out.")
    return redirect("/")


@app.route("/new-med")
def add_new_med():
    """Shows form to add new medication information."""

    return render_template("new-med.html")


@app.route("/new-med-success", methods=["POST"])
def handle_med_info():
    """Handles new medication submission."""

    # Get user ID
    user = session['Logged in user']
    user_id = db.session.query(User.user_id).filter(User.user_id == user).one()

    # Get medication name and dose from form submission and create new instance in Medication table.
    med_name = request.form.get("med-name")
    med_dose = int(request.form.get("med-dose"))

    # Create new instance in Medication table and get med_id.
    new_med = Medication(name=med_name, dose=med_dose)
    db.session.add(new_med)
    db.session.commit
    med_id = db.session.query(Medication.med_id).filter((Medication.name == med_name) & (Medication.dose == med_dose)).one()

    # Get start and end dates and convert them to datetime objects.
    start_date = request.form.get("start-date")
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = request.form.get("end-date")
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    frequency = request.form.get("frequency")

    if frequency == 'everyday':
        new_freq = Frequency(user_id=user_id, med_id=med_id, cycle_length=1,
                             start_date=start_date, end_date=end_date)
        db.session.add(new_freq)
        db.session.commit()

        freq_id = db.session.query(Frequency.freq_id).filter((Frequency.user_id == user_id) & (Frequency.med_id == med_id)).one()

        times_per_day = int(request.form.get("etimes_per_day"))

        for i in range(times_per_day):
            time = request.form.get("everyday-time-" + str(i))
            time = datetime.strptime(time, '%H:%M')
            reminder = request.form.get("everyday-remind-" + str(i))
            if reminder == "yes":
                reminder = True
            else:
                reminder = False
            new_comp = Compliance(freq_id=freq_id, offset=0, sched_time=time, reminder=reminder)
            db.session.add(new_comp)
            db.session.commit()

    if frequency == 'day-interval':

        cycle_length = request.form.get("interval")

        new_freq = Frequency(user_id=user_id, med_id=med_id, cycle_length=cycle_length,
                             start_date=start_date, end_date=end_date)
        db.session.add(new_freq)
        db.session.commit()

        freq_id = db.session.query(Frequency.freq_id).filter((Frequency.user_id == user_id) & (Frequency.med_id == med_id)).one()

        times_per_day = int(request.form.get("itimes_per_day"))

        for i in range(times_per_day):
            time = request.form.get("interval-time-" + str(i))
            time = datetime.strptime(time, '%H:%M')
            reminder = request.form.get("interval-remind-" + str(i))
            if reminder == "yes":
                reminder = True
            else:
                reminder = False
            new_comp = Compliance(freq_id=freq_id, offset=0, sched_time=time, reminder=reminder)
            db.session.add(new_comp)
            db.session.commit()

    if frequency == 'specific-days':

        new_freq = Frequency(user_id=user_id, med_id=med_id, cycle_length=7,
                             start_date=start_date, end_date=end_date)
        db.session.add(new_freq)
        db.session.commit()

        freq_id = db.session.query(Frequency.freq_id).filter((Frequency.user_id == user_id) & (Frequency.med_id == med_id)).one()

        times_per_day = int(request.form.get("stimes_per_day"))

        # Determine which day(s) are checked.
        weekdays = request.form.getlist('day')  # Returns a list of integers

        # Get weekday of start date.
        start_day = start_date.weekday()

        # Create for loop for each specific day selected.
        for day in weekdays:

            # Calculate offset by comparing datetime object to start date.
            offset = int(day) - start_day
            for i in range(times_per_day):
                time = request.form.get("specific-time-" + str(i))
                time = datetime.strptime(time, '%H:%M')
                reminder = request.form.get("specific-remind-" + str(i))
                if reminder == "yes":
                    reminder = True
                else:
                    reminder = False
                new_comp = Compliance(freq_id=freq_id, offset=offset, sched_time=time, reminder=reminder)
                db.session.add(new_comp)
                db.session.commit()

    flash("New medication added to your list.")
    return redirect(url_for('show_user_page',
                            user_id=session['Logged in user']))


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
