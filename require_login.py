"""
Protect routes with firebase.
"""
import pyrebase
from firebase_admin import credentials, auth, initalize_app
import json
import functools

#Connect to firebase
cred = credentials.Certificate('creds.json')
firebase = initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open('creds.json')))

def require_login(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        
        val = func(*args, **kwargs)
        return val