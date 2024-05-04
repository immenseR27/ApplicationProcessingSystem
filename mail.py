import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

FROM_EMAIL = 'abricos.group.hr@gmail.com'
PASSWORD = 'abmexazlqxwfdqwh'

def parse_template(file_name):
    with open(file_name, 'r', encoding='utf-8') as msg_template:
        msg_template_content = msg_template.read()
    return Template(msg_template_content)

def send_invitation(mail, name, patronymic, position, date, time):
    message_template = parse_template('invitation.txt')

    smtp_server = smtplib.SMTP(host='smtp.gmail.com', port=587)
    smtp_server.starttls()
    smtp_server.login(FROM_EMAIL, PASSWORD)

    message = message_template.substitute(CANDIDATE_NAME=name, CANDIDATE_PATRONYMIC=patronymic, CANDIDATE_POSITION=position, INTERVIEW_DATE=date, INTERVIEW_TIME=time)

    multipart_msg = MIMEMultipart()
    multipart_msg['From'] = FROM_EMAIL
    multipart_msg['To'] = mail
    multipart_msg['Subject'] = "Приглашение на собеседование"
    multipart_msg.attach(MIMEText(message, 'plain'))

    smtp_server.send_message(multipart_msg)
    del multipart_msg

    smtp_server.quit()
