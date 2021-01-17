"""
Protect routes with firebase.
"""
import pyrebase
from firebase_admin import credentials, auth, initialize_app
import json
from flask import request
import functools

#Connect to firebase
cred = credentials.Certificate('creds.json')
firebase = initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open('creds.json')))

def require_login(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not request.headers.get('authorization'):
            return {'message': 'No token provided'},400
        try:
            user = auth.verify_id_token(request.headers['authorization'])
        except:
            return {'message':'Invalid token provided.'},400
        return func(*args, user, **kwargs)
    return wrapper