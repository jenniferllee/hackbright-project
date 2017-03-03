from jinja2 import StrictUndefined
from flask import (Flask, jsonify, render_template, redirect, request, flash,
                   session)
from flask_debugtoolbar import DebugToolbarExtension
from model import (User, Medication, Frequency, Compliance, Drug,
                   connect_to_db, db)
import datetime
import json

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
    """Sign up for an account or login with an existing account."""

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
            session["Logged in user"] = user.user_id
            flash("Welcome, " + user.fname + "! You are logged in.")
            return redirect("/user")

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

    # Get name, email, phone, and password from registration form submission.
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")

    user = db.session.query(User).filter(User.email == email).first()

    # If user email already exists, redirect to login page.
    if user:
        flash("You are already registered. Please log in.")
        return redirect("/login")

    # Otherwise, add new user to database and redirect to login page.
    else:
        new_user = User(fname=fname, lname=lname, email=email, phone=phone, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account successfully created! Please log in.")
        return redirect("/login")


@app.route("/user")
def show_user_page():
    """Displays individual user page with all medications for the user.
    User has the option to add or remove medications.
    """

    user_id = session['Logged in user']

    # Get all the frequencies for the user.
    frequencies = Frequency.query.filter_by(user_id=user_id).all()

    frequency_list = []

    # Query name, dose, day, and time for each of the user's medications, and append query object to frequency_list.
    for frequency in frequencies:

        # Query medication information
        med = Medication.query.get(frequency.med_id)
        frequency.name = med.name
        frequency.dose = med.dose
        frequency.unit = med.unit

        # Query scheduled day, time, and whether a reminder is set for the medication.
        frequency.times = set([(compliance.sched_time.strftime('%I:%M %p'),
                                compliance.reminder) for compliance in Compliance.query.filter_by(freq_id=frequency.freq_id).all()])
        if frequency.days == 'Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday':
            frequency.days = 'Everyday'

        frequency_list.append(frequency)

    return render_template("user.html", user_id=user_id, frequencies=frequency_list)


@app.route("/user/today")
def show_todays_meds():
    """Displays the medications that need to be taken for the day.
    User has the option to mark each dose as taken.
    """

    user_id = session['Logged in user']

    # Today's date for template display.
    today = datetime.datetime.strftime(datetime.datetime.now(), '%A, %B %d %Y')

    # Today's date as a date object.
    todays_date = datetime.datetime.now().date()

    # Get all the frequencies for the user.
    frequencies = Frequency.query.filter_by(user_id=user_id).all()

    # Query name, dose, and scheduled time for medications user is scheduled to take today.
    frequency_list = []

    for frequency in frequencies:
        is_today = False
        compliances = Compliance.query.filter(Compliance.freq_id == frequency.freq_id).all()
        for compliance in compliances:
            if compliance.sched_time.date() == todays_date:
                is_today = True

                med = Medication.query.get(frequency.med_id)
                frequency.name = med.name
                frequency.dose = med.dose
                frequency.unit = med.unit
                compliance_filter = Compliance.query.filter(Compliance.freq_id == frequency.freq_id).all()
                frequency.times = [(compliance.sched_time.strftime('%I:%M %p'), compliance.comp_id, compliance.actual_time) for compliance in compliance_filter if compliance.sched_time.date() == todays_date]
        if is_today:
            frequency_list.append(frequency)

    return render_template("today.html", today=today, frequencies=frequency_list)


@app.route("/user/today/taken", methods=["POST"])
def changeCompliance():
    """Adds taken information to compliance table."""

    # Retrieve compliance from AJAX request.
    comp_id = int(request.form.get("comp_id"))
    taken = request.form.get("taken")

    # Update database to reflect compliance.
    comp = Compliance.query.get(comp_id)
    comp.actual_time = taken

    db.session.commit()

    return "taken changed"


@app.route("/user/compliance")
def show_compliance():
    """Shows graph of user's medication compliance for a given time frame."""

    # Today's date for template display.
    today = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')

    return render_template('compliance.html', today=today)


@app.route("/user/compliance.json", methods=["GET"])
def display_compliance_chart():
    """Gets date range and return chart data about user compliance."""

    comp_start = request.args.get("comp-start")
    comp_start = datetime.datetime.strptime(comp_start, "%Y-%m-%d").date()
    print comp_start
    comp_end = request.args.get("comp-end")
    comp_end = datetime.datetime.strptime(comp_end, "%Y-%m-%d").date()
    print comp_end

    user_id = session['Logged in user']
    frequencies = Frequency.query.filter_by(user_id=user_id).all()

    taken = []
    not_taken = []

    for frequency in frequencies:
        comp_true = Compliance.query.filter((Compliance.freq_id == frequency.freq_id) & (Compliance.actual_time)).all()
        for comp in comp_true:
            if comp.sched_time.date() >= comp_start and comp.sched_time.date() <= comp_end:
                taken.append(comp)

    for frequency in frequencies:
        comp_false = Compliance.query.filter((Compliance.freq_id == frequency.freq_id) & (Compliance.actual_time == False)).all()
        for comp in comp_false:
            if comp.sched_time.date() >= comp_start and comp.sched_time.date() <= comp_end:
                not_taken.append(comp)

    num_taken = len(taken)
    num_not_taken = len(not_taken)
    print num_taken
    print num_not_taken

    data_dict = {
        "labels": [
            "Taken",
            "Not Taken"
        ],
        "datasets": [
            {
                "data": [num_taken, num_not_taken],
                "backgroundColor": [
                    "#FF6384",
                    "#36A2EB",
                ],
                "hoverBackgroundColor": [
                    "#FF6384",
                    "#36A2EB",
                ]
            }]
    }

    return jsonify(data_dict)


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

    drugs = db.session.query(Drug.drug_name).all()

    return render_template("new-med.html", drugs=drugs)


@app.route("/drug-names.json")
def get_drug_names():
    """Get drug names."""

    drugs = db.session.query(Drug.drug_name).all()
    drug_names = []
    for drug in drugs:
        drug_names.append(drug[0])

    return json.dumps(drug_names)


@app.route("/new-med-success", methods=["POST"])
def handle_med_info():
    """Handles new medication submission."""

    # Get user ID
    user_id = session['Logged in user']

    # Get medication name and dose from form submission and create new instance in Medication table.
    med_name = request.form.get("med-name")
    med_dose = int(request.form.get("med-dose"))
    med_unit = request.form.get("unit")

    # Check if medication already exists in DB.
    med = db.session.query(Medication).filter((Medication.name == med_name) & (Medication.dose == med_dose) & (Medication.unit == med_unit)).all()

    # If med returns an empty array, create new instance in Medication table and get med_id.
    if not med:
        new_med = Medication(name=med_name, dose=med_dose, unit=med_unit)
        db.session.add(new_med)
        db.session.commit
        med_id = db.session.query(Medication.med_id).filter((Medication.name == med_name) & (Medication.dose == med_dose) & (Medication.unit == med_unit)).one()

    # If med exists in databse, get med_id from Medication table.
    else:
        med_id = db.session.query(Medication.med_id).filter((Medication.name == med_name) & (Medication.dose == med_dose) & (Medication.unit == med_unit)).one()

    # Get start and end dates and convert them to datetime objects.
    start_date = request.form.get("start-date")
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = request.form.get("end-date")
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    frequency = request.form.get("frequency")

    if frequency == 'everyday':

        new_freq = Frequency(user_id=user_id, med_id=med_id, days='Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday',
                             cycle_length=1, start_date=start_date, end_date=end_date)
        db.session.add(new_freq)
        db.session.commit()

        freq_id = db.session.query(Frequency.freq_id).filter((Frequency.user_id == user_id) &
                                                             (Frequency.med_id == med_id) &
                                                             (Frequency.start_date == start_date) &
                                                             (Frequency.end_date == end_date)).one()

        times_per_day = int(request.form.get("etimes_per_day"))

        date = start_date
        while date >= start_date and date <= end_date:

            for i in range(times_per_day):
                everyday_time = request.form.get("everyday-time-" + str(i))
                print everyday_time
                everyday_time = datetime.datetime.strptime(everyday_time, '%H:%M').time()
                everyday_time = datetime.datetime.combine(date, everyday_time)
                reminder = request.form.get("everyday-remind-" + str(i))
                if reminder == "yes":
                    reminder = True
                else:
                    reminder = False
                new_comp = Compliance(freq_id=freq_id, sched_time=everyday_time, reminder=reminder)
                db.session.add(new_comp)
                db.session.commit()
            date += datetime.timedelta(days=1)

    if frequency == 'specific-days':

        # Determine which day(s) are checked.
        weekdays = request.form.getlist('day')  # Returns a list of the days.
        weekdays = ', '.join(weekdays)

        new_freq = Frequency(user_id=user_id, med_id=med_id, days=weekdays,
                             cycle_length=7, start_date=start_date, end_date=end_date)
        db.session.add(new_freq)
        db.session.commit()

        freq_id = db.session.query(Frequency.freq_id).filter((Frequency.user_id == user_id) &
                                                             (Frequency.med_id == med_id) &
                                                             (Frequency.start_date == start_date) &
                                                             (Frequency.end_date == end_date)).one()

        times_per_day = int(request.form.get("stimes_per_day"))

        # Get weekday integer of start date.
        start_day = start_date.weekday()
        print start_day

        # Convert weekdays back to a list of days.
        weekdays = weekdays.split(', ')

        # Create for loop for each specific day selected.
        for day in weekdays:
            if day == 'Monday':
                day = 0
            if day == 'Tuesday':
                day = 1
            if day == 'Wednesday':
                day = 2
            if day == 'Thursday':
                day = 3
            if day == 'Friday':
                day = 4
            if day == 'Saturday':
                day = 5
            if day == 'Sunday':
                day = 6

            # Calculate offset by comparing day to start day.
            offset = day - start_day
            # print offset

            date = start_date + datetime.timedelta(days=offset)
            while date >= start_date and date <= end_date:
                # print date
                for i in range(times_per_day):
                    specific_time = request.form.get("specific-time-" + str(i))
                    specific_time = datetime.datetime.strptime(specific_time, '%H:%M').time()
                    specific_time = datetime.datetime.combine(date, specific_time)
                    reminder = request.form.get("specific-remind-" + str(i))
                    if reminder == "yes":
                        reminder = True
                    else:
                        reminder = False
                    new_comp = Compliance(freq_id=freq_id, sched_time=specific_time, reminder=reminder)
                    db.session.add(new_comp)
                    db.session.commit()
                date += datetime.timedelta(days=7)

    # if frequency == 'day-interval':

    #     cycle_length = request.form.get("interval")

    #     new_freq = Frequency(user_id=user_id, med_id=med_id, cycle_length=cycle_length,
    #                          start_date=start_date, end_date=end_date)
    #     db.session.add(new_freq)
    #     db.session.commit()

    #     freq_id = db.session.query(Frequency.freq_id).filter((Frequency.user_id == user_id) &
    #                                                          (Frequency.med_id == med_id) &
    #                                                          (Frequency.start_date == start_date) &
    #                                                          (Frequency.end_date == end_date)).one()

    #     times_per_day = int(request.form.get("itimes_per_day"))

    #     for i in range(times_per_day):
    #         interval_time = request.form.get("interval-time-" + str(i))
    #         interval_time = datetime.strptime(interval_time, '%H:%M')
    #         reminder = request.form.get("interval-remind-" + str(i))
    #         if reminder == "yes":
    #             reminder = True
    #         else:
    #             reminder = False
    #         new_comp = Compliance(freq_id=freq_id, offset=0, sched_time=interval_time, reminder=reminder)
    #         db.session.add(new_comp)
    #         db.session.commit()

    flash("New medication added to your list.")
    return "Drug added."


@app.route("/remove-med", methods=['POST'])
def delete_med():
    """Removes medication for a user from the database."""

    user = session['Logged in user']
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")

    # Delete all compliance and frequency rows for specific medication & frequency.
    med_id = request.form.get("med_id")
    freq_id = db.session.query(Frequency.freq_id).filter((Frequency.med_id == med_id) &
                                                         (Frequency.user_id == user) &
                                                         (Frequency.start_date == start_date) &
                                                         (Frequency.end_date == end_date)
                                                         ).all()[0][0]

    Compliance.query.filter(Compliance.freq_id == freq_id).delete()

    Frequency.query.filter((Frequency.med_id == med_id) &
                           (Frequency.user_id == user) &
                           (Frequency.start_date == start_date) &
                           (Frequency.end_date == end_date)
                           ).delete()

    db.session.commit()

    return "Medication removed."


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
