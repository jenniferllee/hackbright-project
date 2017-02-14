from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

##############################################################################
# Model definitions


class User(db.Model):
    """User of medication website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    fname = db.Column(db.String(64), nullable=False)
    lname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        """Provide helpful representtion when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)


class Medication(db.Model):
    """Medication information."""

    __tablename__ = "medications"

    med_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    dose = db.Column(db.Integer, nullable=True)
    # init_stock = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Medication med_id=%s name=%s dose=%s>" % (self.med_id,
                                                           self.name,
                                                           self.dose)


class Frequency(db.Model):
    """Medication intake frequency."""

    __tablename__ = "frequencies"

    freq_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.user_id'))
    med_id = db.Column(db.Integer,
                       db.ForeignKey('medications.med_id'))
    cycle_length = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)

    # Define relationship to user
    user = db.relationship("User",
                           backref=db.backref("frequencies",
                                              order_by=freq_id))

    # Define relationship to medication
    medication = db.relationship("Medication",
                                 backref=db.backref("frequencies",
                                                    order_by=freq_id))

    # Define relationship to compliance
    compliance = db.relationship("Compliance",
                                 backref=db.backref("frequencies",
                                                    order_by=freq_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Frequency freq_id=%s med_id=%s times_per_day=%s>" % (self.freq_id,
                                                                      self.med_id,
                                                                      self.times_per_day)


class Compliance(db.Model):
    """What time the user takes each dose."""

    __tablename__ = "compliances"

    comp_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    freq_id = db.Column(db.Integer,
                        db.ForeignKey('frequencies.freq_id'))
    # remind_id = db.Column(db.Integer,
    #                       db.ForeignKey('reminders.remind_id'))
    offset = db.Column(db.Integer, nullable=False)
    sched_time = db.Column(db.DateTime, nullable=False)
    actual_time = db.Column(db.DateTime, nullable=True)
    reminder = db.Column(db.Boolean, nullable=False)

    # # Define relationship to reminder
    # reminder = db.relationship("Reminder",
    #                            backref=db.backref("compliance",
    #                                               order_by=comp_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Compliance comp_id=%s taken=%s>" % (self.comp_id, self.taken)


# class Reminder(db.Model):
#     """Scheduled reminders and what time they are scheduled for."""

#     __tablename__ = "reminders"

#     remind_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     comp_id = db.Column(db.Integer,
#                         db.ForeignKey('compliances.comp_id'))
#     time = db.Column(db.DateTime, nullable=False)

#     def __repr__(self):
#         """Provide helpful representation when printed."""

#         return "<Reminder remind_id=%s time=%s>" % (self.remind_id, self.time)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///tracker'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."


    # Could include seed functionality here without additional seed.py file
    # connect_to_db(app)
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    # # Create tables
    # db.create_all()
