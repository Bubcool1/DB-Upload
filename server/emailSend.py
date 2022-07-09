import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def sendEmail(messageSubject, content):
    message = Mail(
        from_email=os.getenv('FROM_EMAIL'),
        to_emails=os.getenv('TO_EMAIL'),
        subject=messageSubject,
        html_content=content)
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
    except Exception as e:
        print(e.message)