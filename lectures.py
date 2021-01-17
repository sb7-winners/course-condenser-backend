from flask import Blueprint, Flask,request, redirect, url_for
from require_login import require_login
from firebase_admin import firestore
import uuid

lectures_api = Blueprint('lectures_api', __name__)

db = firestore.client()
courses_ref = db.collection('lectures')

@lectures_api.route('/getAllLectures', methods=['GET'])
def read():
    course_id = request.args.get('course_id')
    docs = [doc.to_dict() for doc in courses_ref.where(u'course_id', u'==', course_id).stream()]
    return jsonify(all_todos), 200

@lectures_api.route('/getByTitle', methods=['GET'])
def getByTitle():
    title = request.args.get('title')
    docs = [doc.to_dict() for doc in courses_ref.where(u'title', u'==', title).stream()]
    return jsonify(all_todos), 200
