import os
import sys
import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
from config import basedir
import pickle


key, file = sys.argv[1:]
json_keyfile = os.path.join(basedir, os.environ.get('JSON_KEY_FILE'))
json_key = json.load(open(json_keyfile))
scope = ['https://spreadsheets.google.com/feeds']
credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)
gc = gspread.authorize(credentials)
wks = gc.open_by_key(key)
pickle.dump(wks, open(os.path.join(basedir, file), "wb"))
