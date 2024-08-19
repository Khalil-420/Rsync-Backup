import smtplib
from email.mime.text import MIMEText
from app.core.config import settings
from app.db.notifications_db import *
import threading
import time



class Email():
    def __init__(self):
        self._export = threading.Thread(target=self.email_notification)
        self._export.daemon = True
        self._export.start()

    def put_error(self,error:str):
        add_notification_to_db(error)            
            
    def email_notification(self):
        while True:
            time.sleep(20)
            errors = get_notifications_from_db()
            try: 
                if len(errors) > 0:
                    self.send(subject="Backup Server Error Notification",body="\n".join(errors))
                    clear_notifications()
                    
            except Exception as e:
                print("Failed to send email",e)
                
    def send(self,subject: str, body: str):
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = settings.email_sender
            msg["To"] = settings.email_recipient
            msg["Cc"] = settings.email_cc_recipient

            recipients = [settings.email_recipient] + settings.email_cc_recipient.split(',')

            try:
                with smtplib.SMTP_SSL(settings.email_host, settings.email_port) as server:
                    server.login(settings.email_username, settings.email_password)
                    server.sendmail(settings.email_sender, recipients, msg.as_string())
            except Exception as e:
                print(f"Failed to send email: {e}")


