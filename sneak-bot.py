# -*- coding: utf-8 -*-

#TODO change to python3
#TODO change libray to
# -*- coding: utf-8 -*-
#==== DESCRIPTION ====
#=====================

# This script will send a mail to all recipients in a recipients.dat file if tickets for
# the Berlin CineStar Sneak Prieview (usually Thursday 20:00) are available.
# It will check every 30s if tickets are available and stops when after sending the mails.

# The mail server and authentification uses StartTLS and the the standard Mail server
# from the Freie Univerität Berlin. You can of course modify these for your porpose.

#==== DEFINITIONS ====
#=====================

import urllib
import time
import smtplib
import getpass

def read_htmlSource(URL):
    sock = urllib.urlopen(URL)
    htmlSource = sock.read()
    sock.close()
    return htmlSource

def read_recipients():
    file = open('recipients.dat', 'r')
    recipients = []
    for line in file:
        if line[0] != '#':
            recipients.append(line[:-1])

    return recipients
    file.close()

def auth_mail(user,pwd):
    try:
        server = smtplib.SMTP(serveradress, 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.close()
        return True
    except:
        return False


def send_mail(recipient, subject, body):
    import smtplib

    FROM = user+"@zedat.fu-berlin.de"
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP(serveradress, 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        pass
    except:
        print("Failed to send mail.")

#==== MAIN ====
#==============

serveradress = "mail.zedat.fu-berlin.de"

print("Type in username and password for zedat mail authentification.")

auth = False
while auth == False:
    user = raw_input("username: ")
    pwd = getpass.getpass()
    auth = auth_mail(user,pwd)
    if auth == False:
        print("Server authentification failed. try another username or password or cancel with ctrl+d.")

print("Try every 30s if tickets are available and send a mail to all recipients \
in the recipients.dat file.")

URL = "http://www.cinestar.de/de/kino/berlin-cinestar-original-im-sony-center/veranstaltungen/original-sneak-mysterie-movie-ov/"

#main loop
while True:
    htmlSource = read_htmlSource(URL)
    if htmlSource.find("503 Service Temporarily Unavailable") != -1:
        time.sleep(10) #wait 10 seconds if query is rejected
        continue

    if htmlSource.find("Ticket-Reminder") == -1:
        subject = "Sneak tickets available!"
        body = "Sneak tickets are available. For reserving or buying go to:\n\n"+URL+"\n\nBest,\nSneak-Bot"
        recipients = read_recipients()
        send_mail(recipients,subject,body)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+": Sneak tickets AVAIALABLE and mails sent!")
        break

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+": Sneak tickets not available.")
    time.sleep(30)
