__author__ = 'saurabh'
from pymongo import MongoClient
from flask import Flask, request, jsonify
from datetime import datetime
import os, json

app = Flask(__name__)
dbconn = None

@app.route("/create_user", methods = ['GET', 'POST'])
def create_user():
    global dbconn
    patient = {}
    patient['role'] = 'patient'
    patient['username'] = request.values.get('user')
    patient['password'] = request.values.get('pass')
    patient['name'] = request.values.get('name')
    patient['DOB'] = request.values.get('DOB')
    patient['gender'] = request.values.get('gender')
    patient['phone'] = request.values.get('phone')
    patient['height'] = request.values.get('height')
    patient['weight'] = request.values.get('weight')

    collection = create_db_conn('person')
    collection.insert_one(patient)
    dbconn.close()

@app.route("/patient_login", methods = ['GET', 'POST'])
def patient_login():
    json = {}
    username = request.values.get('user')
    password = request.values.get('pass')

    collection = create_db_conn('person')
    if collection.find_one({'role':'patient','username':username, 'password':password}):
        print('Login Successful!')
        json = collection.find_one({'role':'patient','username':username, 'password':password})
        json['symptoms'] = symptoms_data()
    dbconn.close()
    return jsonify(json)

def symptoms_data():
    if request.method == 'POST':
        collection = create_db_conn('symptoms')
        symptoms_list = collection.find_one()
        return symptoms_list

@app.route("/doctor_login", methods = ['GET', 'POST'])
def doctor_login():
    patient_json_list = []
    patient_json = {}
    username = request.values.get('user')
    password = request.values.get('pass')

    collection = create_db_conn('person')
    if collection.find_one({'role':'doctor', 'username':username, 'password':password}):
        patients = collection.find({'role':'patient', 'doctor':username})
        for patient in patients:
            patient_json['name']= patient['name']
            patient_json['flag'] = patient['riskflag']
            patient_json['phone'] = patient['phone']

            patient_json_list.append(patient_json)
        dbconn.close()
        print(patient_json_list)
        return jsonify({'patient_list':patient_json_list})
    else:
        return None



@app.route("/patient_info", methods = ['GET', 'POST'])
def patient_info():
    patient_json = {}
    patient = request.values.get('patient')
    collection = create_db_conn('person')
    patient_info = collection.find_one({'role':'patient', 'username':patient})
    patient_json['name'] = patient_info['name']
    patient_json['age'] = int(datetime.now().year) - int(patient_info['DOB'].split("-")[2])
    patient_json['weight'] = patient_info['weight']
    patient_json['height'] = patient_info['height']
    patient_json['lastvisitdate'] = patient_info['lastvisitdate']
    patient_json['riskflag'] = patient_json['riskflag']

    collection = create_db_conn('symptoms')
    patient_json['symptom'] = collection.find_one({'patient_username': patient})
    return(jsonify(patient_json))


@app.route("/prescription", methods = ['GET', 'POST'])
def prescription_info():
    prescription_json = {}
    collection = create_db_conn('prescription')
    prescription_json['patientusername'] = collection['patient']
    prescription_json['illness'] = collection['illness']
    prescription_json['medicine'] = collection['medicine']
    prescription_json['dosage'] = collection['dosagefrequency']
    prescription_json['lastdosedatetime'] = collection['lastdosedatetime']
    return jsonify(prescription_json)

@app.route('/test', methods = ['GET', 'POST'])
def test():
    print(request.args.get('item1')+' '+request.args.get('item2'))


def create_db_conn(coll_name):
    global dbconn
    dbconn = MongoClient(host="mongodb://app:app@ds025459.mlab.com:25459/thecompanion")
    db = dbconn.get_database('thecompanion')
    if not db.get_collection(coll_name):
        db.create_collection(coll_name)
    return db.get_collection(coll_name)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
