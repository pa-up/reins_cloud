import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os


def send_py_gmail(
    message_subject , message_body , from_email_smtp_password ,
    from_email , to_email , cc_mail_row_list = [] , file_path = "",
):
    """ メールを送信する関数 """
    msg = MIMEMultipart()
    msg['To'] = to_email
    msg['From'] = from_email
    if cc_mail_row_list !=[]:
        msg['Cc'] = ",".join(cc_mail_row_list)
    msg['Subject'] = message_subject
    msg.attach(MIMEText(message_body))
    # ファイルをメールに添付
    file_name = os.path.basename(file_path)
    with open(file_path , "rb") as f:
        attachment = MIMEApplication(f.read())
    attachment.add_header("Content-Disposition", "attachment", filename = file_name)
    msg.attach(attachment)
    # サーバーを指定しメールを送信
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(from_email, from_email_smtp_password)
    server.send_message(msg)
    server.quit()


