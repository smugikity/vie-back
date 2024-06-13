from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from init import init_data
from bson import ObjectId
from utils import insert_attendee, delete_attendee, create_student_from_json, create_formatted_student
import os
from pymongo import MongoClient
from prometheus_client import Counter, Gauge, generate_latest
import random
import logging
from werkzeug.security import generate_password_hash, check_password_hash

users = {
    "user1": {
        "username": "user1",
        "password": generate_password_hash("user"),  # Hashed password
        "role": "user"
    },
    "admin": {
        "username": "admin",
        "password": generate_password_hash("admin"),  # Hashed password
        "role": "admin"
    }
}

def authenticate(username, password):
    user = users.get(username)
    if not user:
        return False
    return check_password_hash(user["password"], password)

def requires_auth(role="user"):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.authorization  # Get authorization header

            if not auth or not authenticate(auth.username, auth.password):
                abort(401, "Authorization required")

            if role == "admin" and users[auth.username]["role"] != role:
                abort(403, "Admin privileges required")

            return f(*args, **kwargs)
        return decorated
    return decorator


def create_app(students_collection):
    app = Flask(__name__)
    # CORS(app, resources={r"/*": {"origins": "*", "methods": "*", "headers": "Content-Type"}})

    @app.after_request
    def handle_options(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With"
        return response
    @app.route('/')
    def index():
        return "index"

    @app.route('/students', methods=['GET'])
    @requires_auth()
    def handle_students():
        students = list(students_collection.find())
        formatted_students = [create_formatted_student(student) for student in students]
        return jsonify(formatted_students)

    @app.route('/students', methods=['POST'])
    @requires_auth(role="admin")
    def add_students():
        student = create_student_from_json(request.get_json())
        stt = insert_attendee(students_collection, student)
        return jsonify({"stt":stt})


    @app.route('/students/<_id>', methods=['PUT'])
    @requires_auth(role="admin")
    def edit_student(_id):
        student_id = int(_id)
        if student_id is not None:
            student_org = students_collection.find_one({'stt': student_id})
            if student_org:
                student = create_student_from_json(request.get_json())
                students_collection.update_one({"stt": student_id}, {"$set": student})
                return jsonify({'message': 'Student Details Updated Successfully'})

        

    @app.route('/students/<_id>', methods=['DELETE'])
    @requires_auth(role="admin")
    def delete_student(_id):
        student_id = int(_id)
        delete_attendee(students_collection, student_id)
        return jsonify({'message': 'Student Details Deleted Successfully'})
    
    CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')

    number_of_requests = Counter(
        'number_of_requests',
        'The number of requests, its a counter so the value can increase or reset to zero.'
    )

    current_memory_usage = Gauge(
        'current_memory_usage_locally',
        'The current value of memory usage, its a gauge so it can go up or down.',
        ['server_name']
    )

    @app.route('/metrics', methods=['GET'])
    def get_data():
        """Returns all data as plaintext."""
        number_of_requests.inc()
        current_memory_usage.labels('server-a').set(random.randint(10000,90000))
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    @app.after_request
    def log_response_info(response):
        log_message = f"method:{request.method} path:{request.path} code:{response.status_code}"
        app.logger.info(log_message)
        return response

    return app


if __name__ == '__main__':
    MONGODB_DATABASE = os.environ.get("MONGODB_DATABASE")
    MONGODB_HOSTNAME = os.environ.get("MONGODB_HOSTNAME")
    uri = f'mongodb://{MONGODB_HOSTNAME}:27017'
    client = MongoClient(uri)
    db = client[f'{MONGODB_DATABASE}']
    students_collection = db.attendees
    app = create_app(students_collection)
    

    app.run(debug=True, use_debugger=False, use_reloader=False, host="0.0.0.0")
