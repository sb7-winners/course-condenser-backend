from flask import Blueprint, Flask,request, redirect, url_for
from require_login import require_login
from firebase_admin import firestore
import uuid

courses_api = Blueprint('courses_api', __name__)

db = firestore.client()
courses_ref = db.collection('courses')

@courses_api.route('/addCourse', methods=['POST'])
@require_login
def addCourse():
    course_name = request.json["course_name"]
    id = request.args.get('id')
    course_id = uuid.uuid4()

    courses_ref.document(id).set({
        "course_id":course_id,
        "course_name":course_name,
        "user_id":user.user_id
    })

@courses_api.route('/getAllCourses', methods=['GET'])
@require_login
def read():
    user_id = request.args.get('user_id')
    courses = courses_ref.document(user_id).get()
    return jsonify(courses.to_dict()), 200
