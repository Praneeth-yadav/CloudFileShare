from flask import Flask,render_template, request, session, redirect, url_for
import re
import datetime
from flaskext.mysql import MySQL
import os
import boto3
import pymysql
from werkzeug.utils import secure_filename


app=Flask(__name__)
DATABASE_USER = 'admin'
DATABASE_PASSWORD = 'multiweekdb'
DATABASE_DB= 'defaultdb'
DATABASE_HOST= 'multiweekdb.clnopyq3sfwe.us-east-1.rds.amazonaws.com'
DATABASE_PORT= 3306



count=0
@app.route('/')
def base():
    return render_template('Login.html')

@app.route('/Register')
def Register():
    return render_template('Register.html')

@app.route('/Mainpage')
def mainpage():
    return render_template('mainpage.html')

@app.route('/verify',methods=["POST"])
def verify():
    email = request.form.get('email')
    password = request.form.get('Password')
    conn=pymysql.connect(host=DATABASE_HOST,user=DATABASE_USER,password=DATABASE_PASSWORD,database=DATABASE_DB,port=DATABASE_PORT)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM userdetails_peragana WHERE email=%s",email)
    user = cursor.fetchone()
    if user is None:
         message='Email not found'

    elif user[1] != password:
        message='Incorrect password'
    else:
        message='Login successful'
        return redirect(url_for('mainpage'))
    conn.close()

    return render_template('Login.html',message=message)

@app.route('/add',methods=["POST"])
def add():
    email1 = request.form.get('email')
    password1 = request.form.get('Password')
    conn=pymysql.connect(host=DATABASE_HOST,user=DATABASE_USER,password=DATABASE_PASSWORD,database=DATABASE_DB,port=DATABASE_PORT)
    cursor = conn.cursor()
    cursor.execute("Insert into userdetails_peragana (email,password) values (%s,%s);",(email1,password1))
    conn.commit()
    return "User added successfully"

@app.route('/fileupload',methods=["POST"])
def fileupload():
    file = request.files['file']
    f=file.filename.split('\\')[-1]
    s3_file_key = secure_filename(f)
    file.save(s3_file_key)
    email1 = request.form.get('email1')
    email2 = request.form.get('email2')
    email3 = request.form.get('email3')
    email4 = request.form.get('email4')
    email5 = request.form.get('email5')
    description=request.form.get('description')
    aws_access_key_id="ASIARAPYWYDCKFLC3CWU"
    aws_secret_access_key="3RPwbG1d+fGt2ym6ZJV/ITHZ1OPrSc6fKayMJBad"
    aws_session_token="FwoGZXIvYXdzEIL//////////wEaDNrQurwfbIDUgyNE+SLGAQUeHXNxWanbkLhRRnAHIUoApM7ovNULHzZEaJTg/BppFBoyFcW18+q/rpi4YwCfILY7ux4DbF43m3xMxDhiJpwJrHeDws0o2z4DF0OU8vIlFi6IVq46Xe0tOf+KP0euO1xbBx+LjDugFoTPIGPRers5CEFuJkHx7tRtvM9cjKLL0GaO0cKIMZrpp08KyE1c40PKPB9+u+d9lHejakmsDmp/6XFgaoDJM1JJBBODvRrQiqXCGumRA+RbFiV9nqQrx4zwYxmkGyjWpa+mBjItC2b76tdIKBGoptltYTaCZes6JGliMuCVY/qeNlK3+NGt6F4lybb0KTj6sepa"
    s3bucketname="c82801a1763196l4399110t1w069777932-originalbucket-o3aowmctyeo5"
    s3bucketname_txt="c82801a1763196l4399110t1w0697779324-resizedbucket-1c3wqesm5rqf4"
    client_s3 = boto3.client('s3', 
    aws_access_key_id=aws_access_key_id, 
    aws_secret_access_key=aws_secret_access_key, 
    aws_session_token=aws_session_token)
    image_url = f"https://{s3bucketname}.s3.amazonaws.com/{secure_filename(f)}"

    print(email1,email2,email3,email4,email5,f,image_url,description)

    txt_filename = f"{f.split('.')[0]}.txt"
    with open(txt_filename, 'w') as txt_file:
        txt_file.write(f"Emails: {email1}, {email2}, {email3}, {email4}, {email5}\n")
        txt_file.write(f"File URL: {image_url}\n")
        txt_file.write(f"Description: {description}")

    # Upload the text file to the new S3 bucket
    file = open (txt_filename, "r")
    text = file.readlines()
    file.close()
    print(text)
    
    client_s3.upload_file(txt_filename, s3bucketname_txt, txt_filename)



    client_s3.upload_file(s3_file_key,s3bucketname,s3_file_key)
    

   
    # Remove the local text file
    os.remove(txt_filename)

    conn=pymysql.connect(host=DATABASE_HOST,user=DATABASE_USER,password=DATABASE_PASSWORD,database=DATABASE_DB,port=DATABASE_PORT)
    cursor = conn.cursor()
    cursor.execute("Insert into details_peragana(email1,email2,email3,email4,email5,filename,fileurl,description) values(%s,%s,%s,%s,%s,%s,%s,%s)",(email1,email2,email3,email4,email5,f,image_url,description))
    conn.commit()

    return "file uploaded successfully"
    
    




if __name__ == '__main__':
    app.run(debug=True)