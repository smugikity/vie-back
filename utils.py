
def insert_attendee(collection, attendee):
    if collection.find_one(sort=[("stt", -1)]):
        attendee['stt'] = int(collection.find_one(sort=[("stt", -1)])["stt"]) + 1
    else:
        attendee['stt'] = 1
    collection.insert_one(attendee)
    return attendee['stt']


def delete_attendee(collection, attendee_id):
    attendee = collection.find_one({"stt": attendee_id})
    if attendee:
        collection.delete_one({"stt": attendee_id})


def create_student_from_json(json):
    return {
        'name': json.get('name'),
        'gender': json.get('gender'),
        'university': json.get('university'),
    }


def create_formatted_student(student):
    return {
        'stt': student['stt'],
        'name': student['name'],
        'gender': student['gender'],
        'university': student['university'],
    }
