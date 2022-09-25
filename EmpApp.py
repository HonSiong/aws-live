from flask import Flask, render_template, request, redirect, url_for
from pymysql import connections
import os
import boto3
import imghdr
# from flask_mail import Mail, Message
from config import *

app = Flask(__name__,static_folder="templates/assets")
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 465
# app.config['MAIL_USERNAME'] = 'ItachiUeki@gmail.com'
# app.config['MAIL_PASSWORD'] = '591499^^'
# app.config['MAIL_USE_TLS'] = False
# app.config['MAIL_USE_SSL'] = True
# mail = Mail(app)

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

        sqlPic = "SELECT `image_path`, `status` FROM `employee` WHERE status = 'Available'"
        cursor = db_conn.cursor()
        cursor.execute(sqlPic)
        pics = cursor.fetchall()

        sqlList = "SELECT `emp_id`, `first_name`, `last_name`, `email`, `phoneNum`, `pri_skill`, `address`, `image_path`, `position`, `department`, `basicSalary`, `status`, `date_of_birth` FROM `employee` WHERE status = 'Available'"
        cursor = db_conn.cursor()
        cursor.execute(sqlList)
        empList = cursor.fetchall()
        return render_template("index.html", pics=pics, empList=empList)

# @app.route("/emaildb", methods=['POST'])
# def emaildb():
#         email = request.form['email']
#         subject = request.form['subject']
#         message = request.form['message']

#         msg = Message("Hey", sender='ItachiUeki@gmail.com', recipients=email)
#         msg.body = message
#         mail.send(msg)

#         return render_template('emailOutput.html')

######################Employee Page#########################################################
@app.route("/employee", methods=['GET'])
def viewemp():
    
        sqlSelect = "SELECT `emp_id`, `first_name`, `last_name`, `pri_skill`, `address` FROM `employee` WHERE `status` = 'Available'"
        cursor = db_conn.cursor()
        cursor.execute(sqlSelect)
        emps = cursor.fetchall()

        sqlSelect2 = "SELECT `emp_id`, `first_name`, `last_name`, `pri_skill`, `address`, `department` FROM `employee` WHERE `status` = 'Resignation'"
        cursor = db_conn.cursor()
        cursor.execute(sqlSelect2)
        emps2 = cursor.fetchall()

        sqlSelectLeave = "SELECT LE.emp_id, EP.email, EP.department, LE.start_date, LE.day_of_leave, LE.document FROM leaveEmp LE, employee EP WHERE LE.emp_id = EP.emp_id"
        cursor = db_conn.cursor()
        cursor.execute(sqlSelectLeave)
        emps3 = cursor.fetchall()
        return render_template('employee.html', emps=emps, emps2=emps2, emps3=emps3)

#######################Profile Page#########################################################
@app.route("/profile/<empid>")
def profile(empid):
        sqlSelect = "SELECT `emp_id`, `first_name`, `last_name`, `email`, `phoneNum`, `pri_skill`, `address`, `image_path`, `position`, `department`, `basicSalary`, `status`, `date_of_birth` FROM `employee` WHERE emp_id = %s"
        cursor = db_conn.cursor()
        cursor.execute(sqlSelect,empid)
        emp = cursor.fetchone()
        return render_template('profile.html', emp=emp, status=emp[11])

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
       sqlEdit = "SELECT `emp_id`, `first_name`, `last_name`, `email`, `phoneNum`, `pri_skill`, `address`, `image_path`, `position`, `department`, `basicSalary`, `status`, `date_of_birth` FROM `employee` WHERE emp_id = %s"
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
    emp_image_file = request.files['emp_image_file']

    updatesql = "UPDATE `employee` SET `emp_id` = %s, `first_name` = %s, `last_name` = %s, `email` = %s, `phoneNum` = %s, `pri_skill` = %s, `address` = %s, `image_path` = %s, `position` = %s, `department` = %s, `basicSalary` = %s, `status` = %s, `date_of_birth` = %s WHERE `emp_id` = %s"
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
        cursor.execute(updatesql,(emp_id, first_name, last_name, email, phoneNum, pri_skill, address, object_url, position, department, basicSalary, status, date_of_birth, emp_id))
        db_conn.commit()

    finally:
            cursor.close()

    print("all modification done...")
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

    sqlDelete = "UPDATE `employee` SET `status` = 'Resignation' WHERE `emp_id` = %s"
    cursor = db_conn.cursor()
    cursor.execute(sqlDelete,(emp_id))
    db_conn.commit()
    return render_template('delEmpOutput.html', empid=emp_id)

#######################TAKE LEAVE FORM PAGE####################################

@app.route("/leave", methods=['GET', 'POST'])
def leave():
    return render_template('leaveForm.html')

@app.route("/leavedb", methods=['POST'])
def leavedb():

    emp_id = request.form['emp_id']
    start_date = request.form['start_date']
    day_of_leave = request.form['day_of_leave']
    reason = request.form['reason']
    status = "Approved"
    date_of_applied = request.form['date_of_applied']
    emp_document_file = request.files['emp_document_file']

    leavesql = "INSERT INTO leaveEmp (start_date, day_of_leave, reason, status, date_of_applied, document, emp_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_document_file.filename == "":
        return "Please select a file"

    try:

        # Uplaod image file in S3 #
        emp_document_file_name_in_s3 = "emp-id-" + str(emp_id) + "_document_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_document_file_name_in_s3, Body=emp_document_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_document_file_name_in_s3)

        except Exception as e:
            return str(e)
        cursor.execute(leavesql, (start_date, day_of_leave, reason, status, date_of_applied, object_url, emp_id))
        db_conn.commit()

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('leaveOutput.html', empid=emp_id)


    #######################Payroll PAGE####################################
@app.route("/payroll", methods=['GET'])
def payroll():
    
    sqlSelectBasic = "SELECT E.emp_id, E.first_name, E.last_name, E.basicSalary, P.allowance, P.EPF, P.SOCSO, P.monthly_salary FROM employee E, payroll P"
    cursor = db_conn.cursor()
    cursor.execute(sqlSelectBasic)
    emps = cursor.fetchall()


    return render_template('payroll.html', emps=emps)

@app.route("/payrolldb", methods=['POST'])
def payrolldb():
    
    #Calculation 
    emp_id = request.form['emp_id']
    allowance = float(request.form['allowance'])

    sqlSelect = "SELECT emp_id, basicSalary FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(sqlSelect,(emp_id))
    emps = cursor.fetchone()
    
    basicsalary = float(emps[1]) 

    EPF = basicsalary *  0.11
    SOCSO = basicsalary * 0.005
    total = basicsalary + allowance - EPF - SOCSO 


    sqlPayroll = "SELECT * FROM payroll WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(sqlPayroll,emp_id)
    emp = cursor.fetchall()
    if bool(emp):
        sqlUpdate = "UPDATE payroll SET allowance = %s, EPF = %s, SOCSO = %s, monthly_salary = %s WHERE emp_id = %s"
        cursor = db_conn.cursor()
        cursor.execute(sqlUpdate, (allowance, EPF, SOCSO, total, emp_id))
        db_conn.commit()
    else:
        sqlInsert = "INSERT INTO payroll (allowance, EPF, SOCSO, monthly_salary, emp_id) VALUES (%s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()
        cursor.execute(sqlInsert, (allowance, EPF, SOCSO, total, emp_id))
        db_conn.commit()

    return redirect(url_for('payroll'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)