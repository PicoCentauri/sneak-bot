#!/usr/bin/env python3
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

#standard packages
import urllib.request
import time
import smtplib
import getpass
import configparser
import os
import sys

#non-standard packages
from lxml import html
import keyring

def read_htmlSource(URL):
    with urllib.request.urlopen(URL) as response:
        htmlSource = response.read()
    return htmlSource.decode("utf-8")

def get_ticketURL(pagestring):
    tree = html.fromstring(pagestring)
    try:
        split = tree.xpath("//div[@class='table']//a/@href")[0].split('&')[0:2]# cut unnecassy information about the iframe
        ticketURL = "&".join(split)
    except: ticketURL = "not found"

    return ticketURL

def read_recipients():
    scriptpath = os.path.dirname(os.path.realpath(sys.argv[0]))
    file = open(scriptpath+'/recipients.dat', 'r')
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
    DATE = time.strftime("%a, %d %b %Y %H:%M:%S %z",time.localtime())
    # Prepare actual message
    message = """From: %s\nDate: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM,DATE, ", ".join(TO), SUBJECT, TEXT)
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

def read_config():
    path = os.path.join(os.path.expanduser('~'),'.sneak_bot')
    config = configparser.ConfigParser()
    try:
        config.read(os.path.join(path,'config.ini'))
    except: pass
    return config

def write_config():
    path = os.path.join(os.path.expanduser('~'),'.sneak_bot')
    if os.path.exists(path) == False:
        os.mkdir(path)
    config['mail']={'user': user,
                    'password_saved': str(password_saved).lower()}

    with open(os.path.join(path,'config.ini'), 'w') as configfile:
        config.write(configfile)

#==== MAIN ====
#==============
config = read_config()
serveradress = "mail.zedat.fu-berlin.de"

if config.sections() == []:
    #getting username and passowrd for sending mails.

    print("First time of using Sneak-Bot. Type in username and password for zedat mail authentification.")
    auth = False
    while auth == False:
        user = input("username: ")
        pwd = getpass.getpass()
        auth = auth_mail(user,pwd)
        if auth == False:
            print("Server authentification failed. try another username or password or cancel with ctrl+d.")
    print("Do you want to save your password for future usage ?")
    password_saved = input("(y/n): ").lower() in "yes"
    if password_saved == True:
        #TODO add fallback when no keychain is supported
        keyring.set_password("sneak_bot", user, pwd)
    write_config()
else:
    user = config['mail']['user']
    print(config['mail'].getboolean('password_saved'))
    if config['mail'].getboolean('password_saved') == True:
        pwd = keyring.get_password("sneak_bot", user)
    else:
        print("Type password for zedat mail authentification.")
        pwd = getpass.getpass()
print("If you want to reset sneak bot just delete the .sneak_bot folder in your home directory:\n\nrm -r "+
os.path.join(os.path.expanduser('~'),'.sneak_bot')+"\n")
print("Try every 30s if tickets are available and send a mail to all recipients \
in the recipients.dat file.")

#main loop
URL = "http://www.cinestar.de/de/kino/berlin-cinestar-original-im-sony-center/veranstaltungen/original-sneak-mysterie-movie-ov/"
while True:
    try:
        htmlSource = read_htmlSource(URL)
    except urllib.error.URLError as e:
        print(e.reason+": wait 10 seconds before trying again...")
        time.sleep(10) #wait 10 seconds if an error occur
        continue
    if "Ticket-Reminder" not in htmlSource:
        ticketURL = get_ticketURL(htmlSource)

        subject = "Sneak tickets available!"
        body = "Sneak tickets are available. For reserving or buying go to:\n\n"+ticketURL+"\
\n\nMore Information about the CineStar Sneak-Preview at:\n\n"+URL+"\n\nBest,\nSneak-Bot"
        recipients = read_recipients()
        send_mail(recipients,subject,body)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+": Sneak tickets AVAIALABLE and mails sent!")
        break
    else:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+": Sneak tickets not available.")
        time.sleep(30)
