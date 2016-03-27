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

@app.route("/login", methods = ['GET', 'POST'])
def login():
    json = None
    if request.method == 'POST':
        username = request.values.get('user')
        password = request.values.get('pass')

        collection = create_db_conn('patients')
        if collection.find_one({'email':username, 'password':password}):
            print('Login Successful!')
            json = collection.find_one({'email':username, 'password':password})
        else:
            # login failure flag
            print('Login Invalid!')
        dbconn.close()
        return json

@app.route("/patient_symptoms", methods = ['GET', 'POST'])
def symptoms_data():
    if request.method == 'POST':
        collection = create_db_conn('symptoms')
        symptoms_list = collection.find_one()
        return symptoms_list

def create_db_conn(coll_name):
    global dbconn
    dbconn = MongoClient('localhost', 27017)
    db = dbconn.get_database('hackutd')
    if not db.get_collection(coll_name):
        db.create_collection(coll_name)
    return db.get_collection(coll_name)

if __name__ == "__main__":
    app.run(debug=True, port=2020)