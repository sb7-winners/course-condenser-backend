from flask import Blueprint, Flask,request, redirect, url_for
from require_login import require_login
from firebase_admin import firestore
import uuid

courses_api = Blueprint('courses_api', __name__)

db = firestore.client()
courses_ref = db.collection('courses')

@courses_api.route('/addCourse', methods=['POST'])
@require_login
def addCourse(user):
    user_id = user.get("user_id")

    courses = courses_ref.document(user_id).get()
    current_courses = []
    if courses.exists:
        current_courses = courses.get(u"courses")

    current_courses.append({
        'course_name': request.json["course_name"],
        'course_id': str(uuid.uuid4())
    })

    courses_ref.document(user_id).set({
        u"courses": current_courses
    })

    return 200

@courses_api.route('/getAllCourses', methods=['GET'])
@require_login
def read(user):
    user_id = user.get("user_id")

    courses = courses_ref.document(user_id).get()
    if courses.exists:
        return {
            "courses": courses.get(u"courses")
        }, 200
    else:
        return {
            "courses": []
        }, 200