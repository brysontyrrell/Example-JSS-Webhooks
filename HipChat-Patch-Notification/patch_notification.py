import flask
import datetime
import errno
import json
import os
import requests
import shutil
import subprocess
import urllib

HIPCHAT_API_KEY = '<YOUR-V2-API-KEY-HERE>'
HIPCHAT_ROOM_NAME = urllib.quote('<ROOM-NAME-HERE>')

BASEDIR = os.path.abspath(os.path.dirname(__file__))
SOURCE_DIRECTORY = os.path.join(BASEDIR, 'SOURCES')
PACKAGE_DIRECTORY = os.path.join(BASEDIR, 'PACKAGES')

app = flask.Flask('patch-notification')


# This is the route for the inbound webhook:
# http://localhost:5000/patchupdate
# http://localhost:5000/PatchUpdate
# You can define multiple routes to send to one function
@app.route('/patchupdate', methods=['POST'])
@app.route('/PatchUpdate', methods=['POST'])
def patch_update():
    patch = flask.request.get_json()
    notify_new_patch_hipchat(patch['name'], patch['latestVersion'], patch['reportUrl'])

    if patch['name'] == 'Firefox':
        filename = download_firefox(patch['latestVersion'])
        if filename:
            notify_patch_downloaded_hipchat(patch['name'], filename)
            print('Download successful')
            package_name = package_firefox(filename, patch['latestVersion'])
            if package_name:
                notify_patch_packaged_hipchat(patch['name'], package_name)
            else:
                print('The package failed to build')
        else:
            print('The file failed to download')

    return '', 200


# Send a message into the chat room that a new patch is available
def notify_new_patch_hipchat(name, version, url):
    message = "<p>Your JSS has received a new Patch Update <i>(<a href='{}'>Click here to view the report</a>)</i></p>" \
              "<ul>" \
              "<li>Name: <b>{}</b></li>" \
              "<li>Version <b>{}</b></li>" \
              "</ul><br>".format(url, name, version)

    data = {
        'color': 'red',
        'from': 'JSS New Patch Notification',
        'notify': True,
        'message_format': 'html',
        'message': message
    }

    hipchat_room_notification(data)


# Send a message into the chat room that the new version of Firefox has been downloaded
def notify_patch_downloaded_hipchat(name, filename):
    message = "<p><b>'{}'</b> has been downloaded to your <b><i>SOURCES</i></b> directory on the notification server:</p>" \
              "<code>{}</code>".format(name, filename)

    data = {
        'color': 'yellow',
        'from': 'JSS Patch Downloaded',
        'notify': True,
        'message_format': 'html',
        'message': message
    }

    hipchat_room_notification(data)


# Send a message into the chat room that the Firefox package has been built
def notify_patch_packaged_hipchat(name, filename):
    message = "<p>The package for <b>'{}'</b> has been built in your <b><i>PACKAGES</i></b> directory on the notification server:</p>" \
              "<code>{}</code>".format(name, filename)

    data = {
        'color': 'green',
        'from': 'JSS Patch Package Ready',
        'notify': True,
        'message_format': 'html',
        'message': message
    }

    hipchat_room_notification(data)


# Send a message into the chat room using the personal API token
def hipchat_room_notification(message):
    print('Sending HipChat notification')
    r = requests.post(
        'https://api.hipchat.com/v2/room/{}/notification?auth_token={}'.format(HIPCHAT_ROOM_NAME, HIPCHAT_API_KEY),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(message)
    )
    if r.status_code != 204:
        print('There was an error communicating with HipChat: {}\m{}'.format(r.status_code, r.json()))


def get_firefox_download_url():
    r = requests.get('https://www.mozilla.org/en-US/firefox/new/')
    return [u for u in [l for l in r.text.split() if 'https://download.mozilla.org' in l] if 'os=osx' in u][-1].split(
        'data-direct-link=')[-1].replace('"', '')


# This downloads the latest version of Firefox when executed
def download_firefox(version):
    firefox_url = get_firefox_download_url()
    firefox_file = os.path.join(SOURCE_DIRECTORY, 'Firefox_{}_{}.dmg'.format(version, timestamp_now()))

    resp = requests.head(firefox_url, allow_redirects=True)
    urllib.urlretrieve(firefox_url, firefox_file)

    return firefox_file if os.stat(firefox_file).st_size == int(resp.headers['content-length']) else False


# A basic copy function in Python
def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)


# This will convert the downloaded DMG of Firefox into an installable package
def package_firefox(dmg_file, version):
    tmp_dir = '/tmp/firefox_package'
    mnt_dir = '/tmp/firefox_dmg'
    root_dir = os.path.join(tmp_dir, 'root')
    app_dir = os.path.join(root_dir, 'Applications')

    os.makedirs(tmp_dir)
    os.makedirs(app_dir, mode=0777)

    mnt_cmd = ['/usr/bin/hdiutil', 'attach', '-mountpoint', mnt_dir, '-quiet', '-nobrowse', dmg_file]
    print("Mounting the DMG: {}".format(dmg_file))
    print("Command string: {}".format(' '.join(mnt_cmd)))
    subprocess.call(mnt_cmd)
    print("Copying '{}' to package root".format(os.path.join(mnt_dir, 'Firefox.app')))
    copy(os.path.join(mnt_dir, 'Firefox.app'), os.path.join(app_dir, 'Firefox.app'))
    os.chown(app_dir, 0, 80)

    umnt_cmd = ['/usr/bin/hdiutil', 'detach', '-quiet', mnt_dir]
    print("Unmounting the DMG: {}".format(mnt_dir))
    print("Command string: {}".format(' '.join(umnt_cmd)))
    subprocess.call(umnt_cmd)

    package_file = os.path.join(PACKAGE_DIRECTORY, 'Firefox_{}_{}.pkg'.format(version, timestamp_now()))
    pkg_cmd = ['/usr/bin/pkgbuild',
               '--root', root_dir,
               '--identifier', 'com.jamfsw.firefox', '--version', version,
               '--install-location', "/",
               package_file]
    print("Building the package: {}".format(package_file))
    print("Command string: {}".format(' '.join(pkg_cmd)))
    subprocess.call(pkg_cmd)

    shutil.rmtree(tmp_dir)

    return package_file


def timestamp_now():
    """Returns a Unix UTC timestamp"""
    return int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds())


if __name__ == '__main__':
    # Run the Flask app over port 5000 on the localhost
    app.run('0.0.0.0', debug=True)
