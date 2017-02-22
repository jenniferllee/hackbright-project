from model import connect_to_db, db, User, Frequency, Compliance
from datetime import datetime
from twilio.rest import TwilioRestClient
import os


def send_sms(name, phone):

    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    client = TwilioRestClient(account_sid, auth_token)

    message = client.messages.create(to="+1"+phone, from_="+16509357253",
                                     body="Hi %s, remember to take your medicine today!" % (name))


def schedule_reminders(frequency):

    user_name = db.session.query(User.fname).filter(User.user_id == frequency.user_id).first()[0]
    phone = db.session.query(User.phone).filter(User.user_id == frequency.user_id).first()[0]

    today = datetime.today().strftime('%A')

    for day in frequency.get_days():
        if day == '1':
            day = "Monday"
        if day == '2':
            day = "Tuesday"
        if day == '3':
            day = "Wednesday"
        if day == '4':
            day = "Thursday"
        if day == '5':
            day = "Friday"
        if day == '6':
            day = "Saturday"
        if day == '0':
            day = "Sunday"
        if today == day:
            send_sms(user_name, phone)


def main():
    frequencies = db.session.query(Frequency).filter((Compliance.reminder == True) & (Compliance.freq_id == Frequency.freq_id)).all()

    for frequency in set(frequencies):
            schedule_reminders(frequency)


if __name__ == '__main__':

    from server import app
    connect_to_db(app)

    # send_sms('Jennifer', 6508238552)
    main()
