import flask
from flask.ext.sqlalchemy import SQLAlchemy
import json
import os
import requests
from distutils.version import LooseVersion
import urllib

HIPCHAT_API_KEY = '<YOUR-V2-API-KEY-HERE>'
HIPCHAT_ROOM_NAME = urllib.quote('<ROOM-NAME-HERE>')
VERIFY_SSL = False


class Configuration(object):
    APPLICATION_DIR = os.path.dirname(os.path.realpath(__file__))
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}/jss_upgrade.db'.format(APPLICATION_DIR)
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = flask.Flask('jss-upgrade')
app.config.from_object(Configuration)
db = SQLAlchemy(app)


# This object represents the JSS in the database
class JSSRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, index=True, unique=True, nullable=False)
    version = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<JSS {}>'.format(self.url)


# This is the route for the inbound webhook: http://localhost:5000/jss_upgraded
@app.route('/jss_upgraded', methods=['POST'])
def jss_upgraded():
    startup_event = flask.request.get_json()
    if not startup_event and not startup_event['jssUrl']:
        return '', 400

    jss = jss_lookup(startup_event['jssUrl'])

    print('Getting JSS version for: {}'.format(jss.url))
    startup_version = get_jss_version(jss.url)

    if LooseVersion(startup_version) > LooseVersion(jss.version):
        notify_hipchat(jss.version, startup_version, jss.url)
        update_jss_version(jss, startup_version)
    else:
        print("Reported version for JSS '{}' matches version on record".format(jss.url))

    return '', 200


# Find the JSS that sent the inbound webhook in the database and create it if it does not yet exists
def jss_lookup(jss_url):
    result = JSSRecord.query.filter(JSSRecord.url == jss_url).first()
    if not result:
        print("Creating new JSS entry for: {}".format(jss_url))
        try:
            new_jss = JSSRecord(url=jss_url, version=get_jss_version(jss_url))
            db.session.add(new_jss)
            db.session.commit()
        except Exception as e:
            print("Unable to create new JSS record:\n{}".format(e))
            raise

        return new_jss
    else:
        return result


# This method scrapes the version from the login page
def get_jss_version(jss_url):
    r = requests.get(jss_url, verify=VERIFY_SSL)
    for line in str(r.text).split('\n'):
        if line.startswith('  <meta name="version"'):
            return line.translate(None, '<">').split('=')[-1]


# If the JSS that has reported in is at a newer version save that to the database record
def update_jss_version(jss, new_version):
    print("Updating JSS record '{}' with new version: {}".format(jss.url, new_version))
    jss.version = new_version
    db.session.add(jss)
    db.session.commit()


# Send a message into the chat room using the personal API token
def notify_hipchat(previous_version, new_version, jss_url):
    message = "Your JSS has been upgraded from version {} to version {}".format(previous_version, new_version)
    d = {
        'color': 'green',
        'from': 'JSS Upgrade: {}'.format(jss_url),
        'notify': True,
        'message': message
    }

    print('Sending HipChat notification')
    r = requests.post(
        'https://api.hipchat.com/v2/room/{}/notification?auth_token={}'.format(HIPCHAT_ROOM_NAME, HIPCHAT_API_KEY),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(d)
    )
    if r.status_code != 204:
        print('There was an error communicating with HipChat: {}\m{}'.format(r.status_code, r.json()))


if __name__ == '__main__':
    if not os.path.exists(Configuration.SQLALCHEMY_DATABASE_URI):
        # This will create the database file if it does not exist
        db.create_all()

    # Run the Flask app over port 5000 on the localhost
    app.run('0.0.0.0', debug=True)
