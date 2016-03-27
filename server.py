__author__ = 'saurabh'
from pymongo import MongoClient
from flask import Flask, request, jsonify
from datetime import datetime
import os, json, infermedica_api

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
    patient_json = {}
    symptoms_list = []
    username = request.values.get('user')
    password = request.values.get('pass')

    collection = create_db_conn('person')
    if collection.find_one({'role':'patient','username':username, 'password':password}):
        print('Login Successful!')
        patient_info = collection.find_one({'role':'patient','username':username, 'password':password},{'_id':False})

        collection = create_db_conn('symptoms')
        symptoms = collection.find({'patientusername':username},{'_id':False})
        for symptom in symptoms:
            symptoms_list.append(symptom)
        patient_info['symptoms'] = symptoms_list
        dbconn.close()
        print(patient_info)
        return jsonify(patient_info)
    else:
        return None

@app.route("/doctor_login", methods = ['GET', 'POST'])
def doctor_login():
    patient_json_list = []

    username = request.values.get('user')
    password = request.values.get('pass')

    collection = create_db_conn('person')
    if collection.find_one({'role':'doctor', 'username':username, 'password':password}):
        patients = collection.find({'role':'patient', 'doctor':username})
        for patient in patients:
            patient_json = {}
            patient_json['user'] = patient['username']
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

    patient['diagnosis'] = symptom_diagnosis(patient_json['gender'], patient_json['age'], patient)

    collection = create_db_conn('symptoms')
    patient_json['symptom'] = collection.find_one({'patient_username': patient})
    return(jsonify(patient_json))


@app.route("/prescription", methods = ['GET', 'POST'])
def prescription_info():
    prescription_json = []
    collection = create_db_conn('prescription')
    prescriptions = collection.find({'patientusername':request.values.get('user')},{'_id':False})
    for prescription in prescriptions:
        prescription_json.append(prescription)
    return jsonify({'prescriptions':prescription_json})

@app.route("/add_appointment", methods = ['GET', 'POST'])
def appointment():
    collection = create_db_conn('patient')
    collection.update_one({'username':request.values.get('user')}, {"$set": {"nextappointment": request.values.get('appointmentdate')}})

@app.route('/test', methods = ['GET', 'POST'])
def test():
    print(request.args.get('item1')+' '+request.args.get('item2'))

def symptom_diagnosis(gender, age, patientname):
    api = infermedica_api.get_api()
    request = infermedica_api.Diagnosis(sex=gender, age=age)

    collection = create_db_conn('symptom')
    symptoms = collection.find({'patientusername':patientname})
    for symptom in symptoms:
        request.add_symptom(symptoms['symptomid'], 'present')

    # call diagnosis again with updated request
    request = api.diagnosis(request)
    return request

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
