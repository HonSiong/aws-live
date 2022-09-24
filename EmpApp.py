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
def index():
    return render_template("index.html")

######################Employee Page#########################################################
@app.route("/employee", methods=['GET'])
def viewemp():
    
        sqlSelect = "SELECT `emp_id`, `first_name`, `last_name`, `pri_skill`, `address` FROM `employee` WHERE `status` = 'Available'"
        cursor = db_conn.cursor()
        cursor.execute(sqlSelect)
        emps = cursor.fetchall()
        return render_template('employee.html', emps=emps)

#######################Profile Page#########################################################
@app.route("/profile/<empid>")
def profile(empid):
        sqlSelect = "SELECT `emp_id`, `first_name`, `last_name`, `email`, `phoneNum`, `pri_skill`, `address`, `image_path`, `position`, `department`, `basicSalary`, `status`, `date_of_birth` FROM `employee` WHERE emp_id = %s"
        cursor = db_conn.cursor()
        cursor.execute(sqlSelect,empid)
        emp = cursor.fetchone()
        return render_template('profile.html', emp=emp, status=emp.status)

@app.route("/addemp", methods=['GET', 'POST'])
def addemp():
    return render_template('AddEmp.html')


#####################AddEmp Page form############################################################
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
        cursor.execute(insert_sql, (emp_id, first_name, last_name, email, phoneNum, pri_skill, address, object_url, position, department, basicSalary, status, date_of_birth))
        db_conn.commit()

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)
    
########################Edit Profile Page#################################
@app.route("/editProfile", methods=['GET'])
def editemp():
    return render_template('editProfile.html')

@app.route("/editProfile/<empid>")
def editprofile(empid):
       sqlEdit = "SELECT `emp_id`, `first_name`, `last_name`, `email`, `phoneNum`, `pri_skill`, `address`, `position`, `department`, `basicSalary`, `status`, `date_of_birth` FROM `employee` WHERE emp_id = %s"
       cursor = db_conn.cursor()
       cursor.execute(sqlEdit,empid)
       emp = cursor.fetchone()
       return render_template('editProfile.html', emp=emp)

@app.route("/editempdb", methods=['POST'])
def editempdb():
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

    updatesql = "UPDATE `employee` SET `emp_id` = %s, `first_name` = %s, `last_name` = %s, `email` = %s, `phoneNum` = %s, `pri_skill` = %s, `address` = %s, `position` = %s, `department` = %s, `basicSalary` = %s, `status` = %s, `date_of_birth` = %s WHERE `emp_id` = %s"
    cursor = db_conn.cursor()
    cursor.execute(updatesql,(emp_id, first_name, last_name, email, phoneNum, pri_skill, address, position, department, basicSalary, status, date_of_birth, emp_id))
    db_conn.commit()
    
    return render_template('updateOutput.html', empid=emp_id)

######################Delete Employee Page#############################################

@app.route("/deleteEmployee", methods=['GET'])
def deleteEmployee():
    return render_template('deleteEmployee.html')


@app.route("/deleteEmployee/<empid>")
def deleteEmpData(empid):
    sqlSelect = "SELECT `emp_id`, `first_name`, `last_name`, `email` FROM `employee` WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(sqlSelect,empid)
    empD = cursor.fetchone()
    return render_template('deleteEmployee.html', empD=empD)
    

@app.route("/deletempdb", methods=['POST'])
def deletempdb():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']

    sqlDelete = "UPDATE `employee` SET `status` = 'Offline' WHERE `emp_id` = %s"
    cursor = db_conn.cursor()
    cursor.execute(sqlDelete,(emp_id))
    db_conn.commit()
    return render_template('delEmpOutput.html', empid=emp_id)

#######################TAKE LEAVE FORM PAGE####################################
@app.route("/leave", methods=['GET', 'POST'])
def leave():
    return render_template('leaveForm.html')

# @app.route("/leavedb", methods=['POST'])
# def leavedb():

    # leave_id = 1
    # leave_id += 1

    # emp_id = request.form['emp_id']
    # start_date = request.form['start_date']
    # day_of_leave = request.form['day_of_leave']
    # reason = request.form['reason']
    # status = "Approved"
    # date_of_applied = request.form['date_of_applied']
    # document = request.files['document']

    # leavesql = "INSERT INTO leave (leave_id, start_date, day_of_leave, reason, status, date_of_applied, emp_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    # cursor = db_conn.cursor()

    # if document.filename == "":
    #     return "Please select a file"

    # try:

    #     cursor.execute(leavesql, (leave_id, start_date, day_of_leave, reason, status, date_of_applied, emp_id))
    #     db_conn.commit()

    #     # Uplaod image file in S3 #
    #     document_name_in_s3 = "emp-id-" + str(emp_id) + "_document_file"
    #     s3 = boto3.resource('s3')

    #     try:
    #         print("Data inserted in MySQL RDS... uploading image to S3...")
    #         s3.Bucket(custombucket).put_object(Key=document_name_in_s3, Body=document)
    #         bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
    #         s3_location = (bucket_location['LocationConstraint'])

    #         if s3_location is None:
    #             s3_location = ''
    #         else:
    #             s3_location = '-' + s3_location

    #         object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
    #             s3_location,
    #             custombucket,
    #             document_name_in_s3)

    #     except Exception as e:
    #         return str(e)

    # finally:
    #     cursor.close()

    # print("all modification done...")
    # return render_template('leaveOutput.html', empid=emp_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)