from flask import Flask, request, jsonify
from flask_cors import CORS
from init import init_data
from bson import ObjectId
from utils import insert_attendee, delete_attendee, create_student_from_json, create_formatted_student
import os
from pymongo import MongoClient



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
    def handle_students():
        students = list(students_collection.find())
        formatted_students = [create_formatted_student(student) for student in students]
        return jsonify(formatted_students)

    @app.route('/students', methods=['POST'])
    def add_students():
        student = create_student_from_json(request.get_json())
        stt = insert_attendee(students_collection, student)
        return jsonify({"stt":stt})


    @app.route('/students/<_id>', methods=['PUT'])
    def edit_student(_id):
        student_id = int(_id)
        if student_id is not None:
            student_org = students_collection.find_one({'stt': student_id})
            if student_org:
                student = create_student_from_json(request.get_json())
                students_collection.update_one({"stt": student_id}, {"$set": student})
                return jsonify({'message': 'Student Details Updated Successfully'})

        

    @app.route('/students/<_id>', methods=['DELETE'])
    def delete_student(_id):
        student_id = int(_id)
        delete_attendee(students_collection, student_id)
        return jsonify({'message': 'Student Details Deleted Successfully'})
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
