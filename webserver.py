from ftplib import FTP
from flask import Flask, render_template, request
import mysql.connector
from candidate import Candidate
import socket as Socket
import pickle

DB_ADDR = "127.0.0.1"
DB_NAME = 'employment'
DB_USER = 'root'
DB_PWD = '14042000'

APP_ADDR = "127.0.0.1"
APP_PORT = 2000

FTP_ADDR = "127.0.0.1"
FTP_PORT = 1026

HOST = "127.0.0.1"
PORT = 2000

ftp = FTP('')
web = Flask('')

def connect_to_ftp():
    ftp.connect(FTP_ADDR, FTP_PORT)
    ftp.login()

def connect_to_db():
    conn = mysql.connector.connect(host=DB_ADDR, user=DB_USER, password=DB_PWD, database=DB_NAME)
    return conn

def get_vacancies():
    conn = connect_to_db()
    sql = "SELECT position_id, position FROM positions WHERE status=1"
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

def check_existance(phone):
    conn = connect_to_db()
    sql = "SELECT candidate_id FROM candidates WHERE phone = %s"
    cursor = conn.cursor()
    cursor.execute(sql, (phone,))
    result = cursor.fetchall()
    return result

def check_interview(candidate):
    conn = connect_to_db()
    sql = "SELECT * FROM interviews WHERE candidate_id = %s AND position_id = %s"
    cursor = conn.cursor()
    cursor.execute(sql, (candidate.id, candidate.position_id,))
    result = cursor.fetchall()
    return result

def upload_video(video, path):
    connect_to_ftp()
    ftp.storbinary('STOR ' + path + '.mp4', video)
    ftp.quit()

def send_to_app(candidate):
    socket = Socket.socket()
    socket.connect((APP_ADDR, APP_PORT))
    data = pickle.dumps(candidate)
    socket.sendall(data)
    socket.close()

@web.route('/')
def render_app_page():
    vacancies = get_vacancies()
    return render_template("index.html", option=vacancies)

@web.route('/send', methods=['POST'])
def response():
    candidate = Candidate()
    candidate.position_id = request.form.get("position")
    candidate.surname = request.form.get("surname")
    candidate.name = request.form.get("name")
    candidate.patronymic = request.form.get("patronymic")
    candidate.date_of_birthday = request.form.get("birthday")
    candidate.experience = int(request.form.get("experience"))
    candidate.mail = request.form.get("mail")
    candidate.phone = request.form.get("phone")

    exists = check_existance(candidate.phone)
    if exists:
        candidate.id = exists[0][0]
        invited = check_interview(candidate)
        if invited:
            print("Вы уже приглашены")
        else:
            send_to_app(candidate)
    else:
        video = request.files["video"]
        upload_video(video, candidate.phone)
        send_to_app(candidate)

    return render_app_page()

web.run(port=8080)
