import os
import sys
import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
import pickle
import traceback


basedir = os.path.abspath(os.path.dirname(__file__))
try:
    jk = os.environ.get('JSON_KEY_FILE')
    if jk is None:
        raise TypeError("Nisem dobil jk iz enviromenta!")
    key = sys.argv[1]
    file = key
    json_keyfile = os.path.join(basedir, jk)
    json_key = json.load(open(json_keyfile))
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)
    gc = gspread.authorize(credentials)
    wks = gc.open_by_key(key)
    pickle.dump(wks, open(os.path.join(basedir, file), "wb"))
except Exception as err:
    traceback.print_exc(None, open(os.path.join(basedir, "drive-getter-error.log"), "a"))
    exit(199)
