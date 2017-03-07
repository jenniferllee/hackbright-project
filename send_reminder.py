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
        if today == day:
            send_sms(user_name, phone)


def main():
    frequencies = db.session.query(Frequency).filter((Compliance.reminder) & (Compliance.freq_id == Frequency.freq_id)).all()

    for frequency in frequencies:
            schedule_reminders(frequency)


if __name__ == '__main__':

    from server import app
    connect_to_db(app)

    send_sms('Jennifer', '6508238552')
    main()
