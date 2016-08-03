import flask
from flask_mail import Mail, Message
from threading import Thread
import datetime
import os

JSS_ADDRESS = 'https://your.jss.org'
DESTINATION_EMAIL = 'recipient-address@your.org'


class Configuration(object):
    MAIL_SERVER = 'smtp.your.org'
    MAIL_PORT = 587  # SSL/TLS port
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False  # Disable for POODLE
    MAIL_USERNAME = 'sender@your.org'
    MAIL_PASSWORD = 'secret_password'
    MAIL_DEFAULT_SENDER = 'Your Notifications <noreply@your.org>'


app = flask.Flask(__name__)
app.config.from_object(Configuration)
email = Mail(app)


@app.route('/MobileDeviceEnrolled', methods=['POST'])
def mobile_device_enrolled():
    device = flask.request.get_json()
    if not device:
        return '', 400

    send_email(device['event'], enrolled=True)
    return '', 200


@app.route('/MobileDeviceUnEnrolled', methods=['POST'])
def mobile_device_unenrolled():
    device = flask.request.get_json()
    if not device:
        return '', 400

    send_email(device['event'], enrolled=False)
    return '', 200


def build_email_body(data):
    header = 'A mobile device has been enrolled:' if data['enrolled'] else 'A mobile device has been un-enrolled:'
    txt = '''{0},

    Notification received: {1}
    URL to device: {2}

    Device name: {3}
    Device model: {4}
    Serial number: {5}
    '''.format(header, str(data['time']), data['url'], data['name'], data['model'], data['serial'])

    html = '''<p>{0}</p>
    <b>Notification received:</b> {1}
    <br><b>URL to device:</b> <a href={2}>{2}</a>
    <br>
    <br><b>Device name:</b> {3}
    <br><b>Device model:</b> {4}
    <br><b>Serial number:</b> {5}
    '''.format(header, str(data['time']), data['url'], data['name'], data['model'], data['serial'])

    return txt, html


def send_async_email(msg):
    with app.app_context():
        email.send(msg)


def send_email(device_data, enrolled=True):
    subject = 'Mobile Device Enrolled' if enrolled else 'Mobile Device Un-Enrolled'
    email_data = {
        'enrolled': enrolled,
        'name': device_data['deviceName'],
        'model': device_data['model'],
        'serial': device_data['serialNumber'],
        'url': os.path.join('{}/mobileDevices.html?id={}'.format(JSS_ADDRESS, device_data['jssID'])),
        'time': datetime.datetime.utcnow()
    }
    txt, html = build_email_body(email_data)
    msg = Message(
        subject,
        recipients=[DESTINATION_EMAIL]
    )
    msg.body = txt
    msg.html = html
    thr = Thread(target=send_async_email, args=[msg])
    thr.start()


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
