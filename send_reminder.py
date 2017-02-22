from model import connect_to_db, User, Frequency
from datetime import datetime
from twilio.rest import TwilioRestClient
import os


def send_sms(user_name, phone):

    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    client = TwilioRestClient(account_sid, auth_token)

    message = client.messages.create(to="+1%s" % (phone), from_="+16509357253",
                                     body="Hi %s, remember to take your medicine today!" % (user_name))


def schedule_reminders(frequency):

    user_name = User.query.get(User.user_id).fname
    phone = db.session.query(Frequency.user_id)

    today = datetime.today().strftime('%A')

    for day in frequency.get_days():
        if today == day:
            send_sms(user_name, phone)


def main():
    frequencies = db.session.query(Frequency).filter((Compliance.reminder == True) & (Compliance.freq_id == Frequency.freq_id)).all()

    for frequency in frequencies:
            schedule_reminder(frequency)


if __name__ == '__main__':

    from server import app
    connect_to_db(app)

# send_sms('Jennifer', 6508238552)
