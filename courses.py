from flask import Blueprint, Flask,request, redirect, url_for
from require_login import require_login
from firebase_admin import firestore
import uuid

courses_api = Blueprint('courses_api', __name__)

db = firestore.client()
courses_ref = db.collection('courses')

@courses_api.route('/addCourse', methods=['POST'])
def addCourse():
    course_name = request.json["course_name"]
    id = request.args.get('id')
    course_id = uuid.uuid4()

    courses_ref.document(id).set({
        "course_id":course_id,
        'course_name':course_name
    })

@courses_api.route('/getAllCourses', methods=['GET'])
def read():
    todo_id = request.args.get('id')
    todo = todo_ref.document(todo_id).get()
    return jsonify(todo.to_dict()), 200
