from model import connect_to_db, db, Drug, User, Medication, Frequency, Compliance
from server import app


def load_drugs():
    """Load drugs from common-drugs.txt into database."""

    print "Drugs"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    Drug.query.delete()

    # Read u.user file and insert data
    for row in open("data/common-drugs.txt"):
        row = row.rstrip()
        drug_name = row

        drug = Drug(drug_name=drug_name)

        # We need to add to the session or it won't ever be stored
        db.session.add(drug)

    # Once we're done, we should commit our work
    db.session.commit()


def load_users():
    """Load users from users.csv into database."""

    print "Users"

    User.query.delete()

    for row in open("data/users.csv"):
        row = row.rstrip()
        fname, lname, phone, email, password = row.split(",")

        user = User(fname=fname,
                    lname=lname,
                    phone=phone,
                    email=email,
                    password=password)

        db.session.add(user)

    db.session.commit()


def load_medications():
    """Load medications from medications.csv into database."""

    print "Medications"

    Medication.query.delete()

    for row in open("data/medications.csv"):
        # row = row.rstrip()
        name, dose, unit = row.split(",")

        medication = Medication(name=name,
                                dose=dose,
                                unit=unit)
        db.session.add(medication)

    db.session.commit()


def load_frequencies():
    """Load frequencies from frequencies.csv into database."""

    print "Frequencies"

    Frequency.query.delete()

    for row in open("data/frequencies.csv"):
        row = row.rstrip()
        row = row.split(",")

        user_id = int(row[0])
        med_id = int(row[1])
        days = row[2]
        cycle_length = row[3]
        start_date = row[4]
        end_date = row[5]

        frequency = Frequency(user_id=user_id,
                              med_id=med_id,
                              days=days,
                              cycle_length=cycle_length,
                              start_date=start_date,
                              end_date=end_date)

        db.session.add(frequency)

    db.session.commit()


def load_compliances():
    """Load compliances from compliances.csv into database."""

    print "Compliances"

    Compliance.query.delete()

    for row in open("data/compliances.csv"):
        row = row.rstrip()
        freq_id, offset, sched_time, actual_time, reminder = row.split(",")

        if actual_time == "":
            actual_time = None

        compliance = Compliance(freq_id=freq_id,
                                offset=offset,
                                sched_time=sched_time,
                                actual_time=actual_time,
                                reminder=reminder)

        db.session.add(compliance)

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    # Create tables
    db.create_all()

    # Import different types of data
    load_drugs()
    load_users()
    load_medications()
    load_frequencies()
    load_compliances()
