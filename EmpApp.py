from flask import Flask, render_template, request, redirect, url_for
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__,static_folder="templates/assets")

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'

@app.route("/")
def Index():
    return render_template("index.html")

@app.route("/employee", methods=['GET'])
def viewemp():
    
        sqlSelect = "SELECT `emp_id`, `first_name`, `last_name`, `pri_skill`, `address` FROM `employee`"
        cursor = db_conn.cursor()
        cursor.execute(sqlSelect)
        emps = cursor.fetchall()
        return render_template('employee.html', emps=emps)

@app.route("/profile/<empid>")
def profile(empid):
        sqlSelect = "SELECT `emp_id`, `first_name`, `last_name`, `pri_skill`, `address` FROM `employee` WHERE emp_id = %s"
        cursor = db_conn.cursor()
        cursor.execute(sqlSelect,empid)
        emp = cursor.fetchone()
        return render_template('profile.html', emp=emp)

@app.route("/addemp", methods=['GET', 'POST'])
def addemp():
    return render_template('AddEmp.html')


@app.route("/addempdb", methods=['POST'])
def addempdb():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    phoneNum = request.form['phoneNum']
    pri_skill = request.form['pri_skill']
    address = request.form['address']
    position = request.form['position']
    department = request.form['department']
    basicSalary = request.form['basicSalary']
    status = request.form['status']
    date_of_birth = request.form['date_of_birth']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, email, phoneNum, pri_skill, address, position, department, basicSalary, status, date_of_birth))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)
    


##########################################################################
    # @app.route("/editemp", methods=['GET','POST'])
    # def EditEmp():

    #    if request.methods == 'GET':
    #        return render_template('employee.html')
        
    #    if request.methods == 'POST':
    #        mydata = Data.query.get(request.form.get('emp_id'))

    #        mydata.first_name = request.form['first_name']
    #        mydata.last_name = request.form['last_name']
    #        mydata.pri_skill = request.form['pri_skill']
    #        mydata.address = request.form['address']
    #        mydata.emp_image_file = request.files['emp_image_file']

    #        update_sql = "UPDATE employee SET first_name = %s, last_name = %s, pri_skill = %s, location = %s, emp_image_file = %s"
    #        cursor = db_conn.cursor()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)