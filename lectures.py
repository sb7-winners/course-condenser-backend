from flask import Blueprint, Flask,request, redirect, url_for
from require_login import require_login
from firebase_admin import firestore
import uuid
import datetime
import json

lectures_api = Blueprint('lectures_api', __name__)

db = firestore.client()
lectures_ref = db.collection('lectures')
courses_ref = db.collection('courses')

def serializeLecture(lecture):
    return {
        "id": lecture.id,
        "timestamp": lecture.get(u"timestamp"),
        "title": lecture.get(u"title"),
        "url": lecture.get(u"url")
    }

@lectures_api.route('/getAllLectures', methods=['GET'])
@require_login
def read(user):
    query_ref = lectures_ref.where(u"course_id", u"==", request.json["course_id"])
    lectures = [serializeLecture(lecture) for lecture in query_ref.stream()]
        
    return {
        "lectures": lectures
    }, 200

@lectures_api.route('/getLecture', methods=['GET'])
@require_login
def getLecture(user):
    lecture = lectures_ref.document(request.json["lecture_id"]).get()
    if lecture.exists:
        return lecture.to_dict(), 200
    else:
        return {}, 404

@lectures_api.route('/getMostRecents', methods=['GET'])
@require_login
def getByTime(user):
    courses_query_ref = courses_ref.where(u'user_id', u'==', user.get("user_id"))
    docs = [doc.to_dict() for doc in lectures_ref.order_by(u'timestamp', direction=firestore.Query.DESCENDING).limit(5).stream()]
    return json.dumps(docs), 200