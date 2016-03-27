__author__ = 'saurabh'
from pymongo import MongoClient
from flask import Flask, request, render_template

app = Flask(__name__)
dbconn = None

@app.route("/create_user", methods = ['GET', 'POST'])
def create_user():
    global dbconn
    if request.method == 'POST':
        patient = {}
        patient['password'] = request.values.get('pass')
        patient['email'] = request.values.get('email')
        patient['first_name'] = request.values.get('fname')
        patient['last_name'] = request.values.get('lname')
        patient['phone'] = request.values.get('phone')

        collection = create_db_conn('patients')
        collection.insert_one(patient)
        dbconn.close()
    # return render_template("create_user.html")

@app.route("/patient_login", methods = ['GET', 'POST'])
def patient_login():
    json = None
    if request.method == 'POST':
        username = request.values.get('user')
        password = request.values.get('pass')

        collection = create_db_conn('person')
        if collection.find_one({'role':'patient','email':username, 'password':password}):
            print('Login Successful!')
            json = collection.find_one({'role':'patient','email':username, 'password':password})
        else:
            # login failure flag
            print('Login Invalid!')
        json['symptoms'] = symptoms_data()
        dbconn.close()
        return json

def symptoms_data():
    if request.method == 'POST':
        collection = create_db_conn('symptoms')
        symptoms_list = collection.find_one()
        return symptoms_list

@app.route("/doctor_login", methods = ['GET', 'POST'])
def login():
    patient_json_list = []
    patient_json = {}
    if request.method == 'POST':
        username = request.values.get('user')
        password = request.values.get('pass')

        collection = create_db_conn('person')
        if collection.find_one({'role':'doctor', 'email':username, 'password':password}):
            patients = collection.find_one({'role':'patient', 'doctor':username})
            for patient in patients:
                patient_json['name']= patient['lname']+' '+patient['lname']
                patient_json['stage'] = patient['json']
                patient_json['flag'] = patient['flag']

                patient_json_list.append(patient_json)
            dbconn.close()
            return patient_json_list
        else:
            # login failure flag
            print('Login Invalid!')
            return None

@app.route('/test', methods = ['GET', 'POST'])
def test():
    if request.method == 'GET':
        print(str(request.args.get('item1'))+'\n'+'')


def create_db_conn(coll_name):
    global dbconn
    dbconn = MongoClient('localhost', 27017)
    db = dbconn.get_database('hackutd')
    if not db.get_collection(coll_name):
        db.create_collection(coll_name)
    return db.get_collection(coll_name)

if __name__ == "__main__":
    app.run(debug=True, port=2020)
