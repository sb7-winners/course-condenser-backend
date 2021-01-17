from flask import Blueprint, Flask,request, redirect, url_for
from require_login import require_login
from firebase_admin import firestore
import uuid
import datetime
import json

lectures_api = Blueprint('lectures_api', __name__)

db = firestore.client()
lectures_ref = db.collection('lectures')

@lectures_api.route('/getAllLectures', methods=['GET'])
@require_login
def read(user):
    course_id = request.args.get('course_id')
    docs = [doc.to_dict() for doc in lectures_ref.where(u'course_id', u'==', course_id).stream()]
    return docs.__dict__, 200

@lectures_api.route('/getByTitle', methods=['GET'])
@require_login
def getByTitle(user):
    title = request.args.get('title')
    docs = [doc.to_dict() for doc in lectures_ref.where(u'title', u'==', title).stream()]
    return docs.__dict__, 200

@lectures_api.route('/getMostRecents', methods=['GET'])
@require_login
def getByTime(user):
    print(user.get("user_id"))
    docs = [doc.to_dict() for doc in lectures_ref.order_by(u'timestamp', direction=firestore.Query.DESCENDING).limit(5).stream()]
    return json.dumps(docs), 200
