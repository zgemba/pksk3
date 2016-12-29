import json
import os
import pickle
import sys
import traceback

import gspread
from oauth2client.service_account import ServiceAccountCredentials

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
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    gc = gspread.authorize(credentials)
    wks = gc.open_by_key(key)
    pickle.dump(wks, open(os.path.join(basedir, file), "wb"))
except Exception as err:
    traceback.print_exc(None, open(os.path.join(basedir, "drive-getter-error.log"), "a"))
    exit(199)
