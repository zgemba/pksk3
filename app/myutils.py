import os
import pickle
import subprocess

from flask import current_app


# from oauth2client.service_account import ServiceAccountCredentials


def allowed_file(filename):
    return '.' in filename and \
           filename.lower().rsplit('.', 1)[1] in current_app.config["ALLOWED_EXTENSIONS"]


def make_unique_filename(filename):
    if not os.path.exists(filename):
        return filename
    version = 1
    path = os.path.split(filename)[0]
    while True:
        (name, ext) = os.path.splitext(os.path.basename(filename))
        new_file = os.path.join(path, name + str(version) + ext)
        if not os.path.exists(new_file):
            break
        version += 1
    # noinspection PyUnboundLocalVariable
    return new_file


def get_from_gdrive(key):
    getter = current_app.config["GDRIVE_GETTER"]
    return getter(key)


# def get_from_gdrive_local(key):
#    basedir = current_app.config["BASEDIR"]
#    json_keyfile = os.path.join(basedir, current_app.config["JSON_KEY_FILE"])
#    scope = ['https://spreadsheets.google.com/feeds']
#    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
#
#    gc = gspread.authorize(credentials)
#    wks = gc.open_by_key(key)
#    return wks


def get_from_gdrive_remote(key):
    """ DEPRECATED """
    basedir = current_app.config["BASEDIR"]

    # Apache SSL fookup workaround, pohandlam exit code za msgflash
    ec = subprocess.check_call([os.path.join(basedir, "dget.sh"), key, key])
    if ec != 0:
        return ec

    with open(os.path.join(basedir, key), "rb") as dump:
        wks = pickle.load(dump)
    # zbrišem pickle file
    os.remove(os.path.join(basedir, key))
    return wks
