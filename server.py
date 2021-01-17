from flask import Flask
from processLecture import process_lecture
from courses import courses_api
from lectures import lectures_api

app = Flask(__name__)

app.register_blueprint(process_lecture)
app.register_blueprint(courses_api)
app.register_blueprint(lectures_api)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == '__main__':
	app.run(debug=True)
