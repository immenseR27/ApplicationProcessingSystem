import os
import numpy as np
from PIL import Image
import mysql.connector
from ftplib import FTP
import io
from tensorflow import keras
from moviepy.audio.io.AudioFileClip import AudioFileClip
import preprocessing as prep
import mail
import socket as Socket
import pickle
from decimal import Decimal
from datetime import date, timedelta, time

DB_ADDR = "127.0.0.1"
DB_NAME = 'employment'
DB_USER = 'root'
DB_PWD = '14042000'

FTP_ADDR = "127.0.0.1"
FTP_PORT = 1026

HOST = "127.0.0.1"
PORT = 2000

ftp = FTP('')

def connect_to_ftp():
	ftp.connect(FTP_ADDR, FTP_PORT)
	ftp.login()

def connect_to_db():
	conn = mysql.connector.connect(host=DB_ADDR, user=DB_USER, password=DB_PWD, database=DB_NAME)
	return conn

def insert_candidate_into_db(candidate):
	conn = connect_to_db()
	sql = "INSERT INTO candidates (surname, name, patronymic, date_of_birthday, experience, mail, phone, photo, extraversion, " \
		  "openness, agreeableness, neuroticism, conscientiousness) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
	val = [(candidate.surname, candidate.name, candidate.patronymic, candidate.date_of_birthday, candidate.experience,
			candidate.mail, candidate.phone, candidate.photo, Decimal(float(candidate.extraversion)),
			Decimal(float(candidate.openness)),
			Decimal(float(candidate.agreeableness)), Decimal(float(candidate.neuroticism)),
			Decimal(float(candidate.conscientiousness)))]
	cursor = conn.cursor()
	cursor.executemany(sql, val)
	conn.commit()

def insert_interview_into_db(candidate_id, position_id, interview_date, interview_time):
	conn = connect_to_db()
	sql = "INSERT INTO interviews (candidate_id, position_id, interview_date, interview_time) VALUES ( %s, %s, %s, %s)"
	val = [(candidate_id, position_id, interview_date, interview_time)]
	cursor = conn.cursor()
	cursor.executemany(sql, val)
	conn.commit()

def get_vacancies():
	conn = connect_to_db()
	sql = "SELECT position_id, position FROM positions WHERE status=1"
	cursor = conn.cursor()
	cursor.execute(sql)
	result = cursor.fetchall()
	return result


def get_requirements(position_id):
	conn = connect_to_db()
	sql = "SELECT min_experience, min_extraversion, max_neuroticism, min_agreeableness, min_conscientiousness, min_openness FROM positions WHERE position_id=%s"
	cursor = conn.cursor()
	cursor.execute(sql, (position_id,))
	result = cursor.fetchall()
	return result

def get_last_interview():
	conn = connect_to_db()
	sql = "SELECT interview_date, interview_time FROM interviews ORDER BY interview_date DESC, interview_time DESC  LIMIT 1"
	cursor = conn.cursor()
	cursor.execute(sql)
	result = cursor.fetchall()
	if not result:
		return date.today(), timedelta(hours=10)
	else:
		return result[0][0], result[0][1]

def get_position_name(position_id):
	conn = connect_to_db()
	sql = "SELECT position FROM positions WHERE position_id=%s"
	cursor = conn.cursor()
	cursor.execute(sql, (position_id,))
	result = cursor.fetchall()
	return result[0][0]

def get_candidate_id(phone):
	conn = connect_to_db()
	sql = "SELECT candidate_id FROM candidates WHERE phone=%s"
	cursor = conn.cursor()
	cursor.execute(sql, (phone,))
	result = cursor.fetchall()
	return result[0][0]

def get_prediction_from_db(candidate_id):
	conn = connect_to_db()
	sql = "SELECT extraversion, neuroticism, agreeableness, conscientiousness, openness FROM candidates WHERE candidate_id=%s"
	cursor = conn.cursor()
	cursor.execute(sql, (candidate_id,))
	result = cursor.fetchall()
	return result

def upload_photo(photo, path):
	connect_to_ftp()
	image = Image.fromarray(np.uint8(photo)).convert('RGB')
	temp = io.BytesIO()
	image.save(temp, format="jpeg")
	_ = temp.getvalue()
	temp.seek(0)
	ftp.storbinary('STOR ' + path, temp)
	ftp.quit()

def delete_files(audiopath, videopath):
	if os.path.exists (audiopath):
		os.remove(audiopath)
	if os.path.exists(videopath):
		os.remove(videopath)
	return

def get_video(videopath, phone):
	connect_to_ftp()
	video = phone + ".mp4"
	videofile = open(videopath, 'wb')
	ftp.retrbinary('RETR ' + video, videofile.write)
	ftp.quit()

def get_new_prediction(audiopath, videopath):
	AudioFileClip(videopath).write_audiofile(audiopath)
	preprocessed_audio = prep.audio_preprocessing(audiopath)
	extracted_frames = prep.extract_videoframes(filepath=videopath, samples_num=6)
	resized_images = [prep.resize_image(image=frame, new_size=(248, 140)) for frame in extracted_frames]
	cropped_images = [prep.crop_image(image=resized) / 255.0 for resized in resized_images]
	preprocessed_video = np.stack(cropped_images)

	data = []
	data.append(preprocessed_audio)
	data.append(preprocessed_video)

	x0_list = []
	x1_list = []

	x0_list.append(data[0])
	x1_list.append(data[1])

	model_loaded = keras.models.load_model('D:/model3.h5')
	prediction = model_loaded.predict(x=[np.stack(x0_list), np.stack(x1_list)])
	return (prediction)

def check_compliance(prediction, position_id, experience):
	suitable = False
	requirements = get_requirements(position_id)

	print("extraversion: " + str(prediction[0][0]))
	print("agreeableness: " + str(prediction[0][2]))
	print("conscientiousness: " + str(prediction[0][3]))
	print("openness: " + str(prediction[0][4]))
	print("neuroticism: " + str(prediction[0][1]))

	if experience >= requirements[0][0]:
		suitable = True
		for i in range(0, 5):
			req_trait = requirements[0][i + 1]
			pred_trait = round(prediction[0][i], 2)
			if i == 1:
				if pred_trait > float(req_trait):
					suitable = False
			else:
				if pred_trait < float(req_trait):
					suitable = False
	print(suitable)
	return suitable

def get_datetime(last_date, last_time):
	today = date.today()
	interview_date = last_date
	hours = last_time
	if (interview_date <= today) | (date is None):
		if today.weekday() == 5:
			interview_date = today + timedelta(days=2)
		if today.weekday() == 6:
			interview_date = today + timedelta(days=1)
		interview_time = time(10)
	else:
		if (time(last_time) < time(17)):
			interview_time = time(hours + 1)
		else:
			interview_date = interview_date + timedelta(days=1)
			interview_time = time(10)
			get_datetime(interview_date, interview_time)
	return interview_date, interview_time

def invite_candidate(candidate):
	print("invitation...")
	position = get_position_name(candidate.position_id)
	last_date, last_time = get_last_interview()
	hours = last_time.seconds // 3600
	interview_date, interview_time = get_datetime(last_date, hours)
	datelist = str(interview_date).split('-')
	strdate = datelist[2] + '.' + datelist[1] + '.' + datelist[0]
	print(strdate)
	strtime = str(interview_time.hour) + ":00"
	if candidate.id == 0:
		insert_candidate_into_db(candidate)
		candidate.id = get_candidate_id(candidate.phone)
	insert_interview_into_db(candidate.id, candidate.position_id, interview_date, interview_time)
	mail.send_invitation(candidate.mail, candidate.name, candidate.patronymic, position, strdate, strtime)

socket = Socket.socket()
socket.bind((HOST, PORT))
socket.listen()

all_data = bytearray()
while True:
	connection, client_address = socket.accept()
	print('connection from', client_address)
	while True:
		data = connection.recv(1024)
		if data:
			all_data += data
			obj = pickle.loads(all_data)
			candidate = obj
			path = "D:/current_data/ " + candidate.phone
			videopath = path + ".mp4"
			audiopath = path + ".wav"

			if candidate.id == 0:
				get_video(videopath, candidate.phone)
				prediction = get_new_prediction(audiopath, videopath)
				candidate.photo = candidate.phone + ".jpg"
				photo = prep.extract_videoframes(videopath, 1)[0]
				upload_photo(photo, candidate.photo)
			else:
				prediction = get_prediction_from_db(candidate.id)

			suitable = check_compliance(prediction, candidate.position_id, candidate.experience)
			if suitable:
				candidate.extraversion = prediction[0][0]
				candidate.neuroticism = prediction[0][1]
				candidate.agreeableness = prediction[0][2]
				candidate.conscientiousness = prediction[0][3]
				candidate.openness = prediction[0][4]
				invite_candidate(candidate)
			delete_files(audiopath, videopath)