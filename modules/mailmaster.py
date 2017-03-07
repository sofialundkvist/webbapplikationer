# *-* coding:utf-8 *-*
#!/usr/bin/python
import time
import random, string
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import json
from string import Template
import urllib.request

fileIn = open('keys.json', 'r')
dataRead = json.load(fileIn)
fileIn.close()
mail_password = dataRead[0]['mail_password']
mail_user = dataRead[0]['mail_user']


class Mailmaster():
    @classmethod
    def send(cls, mail, message):
        fromaddr = "massa@avmediaskane.se"
        toaddr = mail
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Tack för din anmälan!"
        html_file= open('templates/mail.html', 'r')
        html_content = html_file.read()
        html_file.close()

        replace=[
            {'old':'{name}',
            'new':message['name']},
            {'old':'{img}',
            'new':message['qr']},
            {'old':'{link}',
            'new':message['link']},
            {'old':'{front_end_id}',
            'new':message['front_end_id']}
        ]
        for item in replace:
            html_content = html_content.replace(item['old'],item['new'])
        msg.attach(MIMEText(html_content, 'html'))
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(mail_user, mail_password)
        server.sendmail(fromaddr, toaddr, msg.as_string())
        server.quit()
        return

    @classmethod
    def send_other_mail(cls, mail, message, template, title):
        fromaddr = "massa@avmediaskane.se"
        toaddr = mail
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = title
        html_file= open('templates/'+ template, 'r')
        html_content = html_file.read()
        html_file.close()

        for key, value in message.items():
            html_content = html_content.replace('{'+key+'}',value)

        msg.attach(MIMEText(html_content, 'html'))
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(mail_user, mail_password)
        server.sendmail(fromaddr, toaddr, msg.as_string())
        server.quit()
        return
