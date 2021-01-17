"""
Protect routes with firebase.
"""

from firebase_admin import credentials, auth, initialize_app
import json
from flask import request
import functools

#Connect to firebase
cred = credentials.Certificate('firebase_creds.json')
firebase = initialize_app(cred)


def require_login(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not request.args.get('authorization'):
            return {'message': 'No token provided'},400
        try:
            user = auth.verify_id_token(request.args.get('authorization'))
        except:
            return {'message':'Invalid token provided.'},400
        return func(*args, user, **kwargs)
    return wrapper
