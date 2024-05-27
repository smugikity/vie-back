import unittest
from mongomock import MongoClient
from bson import ObjectId
from app import create_app
from utils import insert_attendee
import logging


def mock_data():
    test_client = MongoClient()
    db = test_client["testdb"]
    test_collection = db["test_collection"]
    if test_collection.estimated_document_count() == 0:
        students = [
            {
                'stt': '1',
                'name': 'haha',
                'username': 'haah',
                'birth_year': '2000',
                'gender': 'Nam',
                'university': 'university',
                'major': 'it'
            },
        ]

        for student in students:
            insert_attendee(test_collection, student)

    return test_collection


class AppTestCase(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()
        self.test_collection = mock_data()
        self.app = create_app(self.test_collection)
        self.app.config["TESTING"] = True
        self.app_client = self.app.test_client()
        self.log = logging.getLogger("LOG")

        self.INIT_COLLECTION_SIZE = self.test_collection.estimated_document_count()
        self.test_student = self.test_collection.find_one({})
        self.new_student = {
            'name': 'haha2',
            'username': 'haha2',
            'birth_year': '2000',
            'gender': 'Nữ',
            'university': 'university2',
            'major': 'it2'
        }

    def tearDown(self):
        self.test_collection.drop()

    def test_index_route(self):
        response = self.app_client.get('/')

        self.assertEqual(response.status_code, 200)

    def test_get_list_students_(self):
        response = self.app_client.get('/students')

        self.assertEqual(response.status_code, 200)

    def test_add_student(self):
        response = self.app_client.post('/students', data=self.new_student)

        self.assertEqual(self.INIT_COLLECTION_SIZE +1, self.test_collection.estimated_document_count())

        result = self.test_collection.find_one({"name": self.new_student["name"]})

        self.assertIsNotNone(result)
        self.assertEqual(result["birth_year"], self.new_student["birth_year"])
        self.assertEqual(result["username"], self.new_student["username"])
        self.assertEqual(result["gender"], self.new_student["gender"])
        self.assertEqual(result["university"], self.new_student["university"])
        self.assertEqual(result["major"], self.new_student["major"])
        self.assertEqual(response.json, {'message': 'Student added successfully'})

    def test_delete_student(self):
        student_id = str(self.test_student['_id'])
        response = self.app_client.delete('/students/' + student_id)

        self.assertEqual(self.INIT_COLLECTION_SIZE -1, self.test_collection.estimated_document_count())

        deleted_student = self.test_collection.find_one({'_id': ObjectId(student_id)})

        self.assertIsNone(deleted_student)
        self.assertEqual(response.json, {'message': 'Student Details Deleted Successfully'})


if __name__ == '__main__':
    unittest.main()
