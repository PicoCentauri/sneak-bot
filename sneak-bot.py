import urllib
import time
import smtplib
import getpass

def read_url(URL):
    sock = urllib.urlopen(URL)
    htmlSource = sock.read()
    sock.close()
    return htmlSource

def read_recipients():
    file = open('recipients.dat', 'r')
    recipients = []
    for line in file:
        recipients.append(line[:-1])
    return recipients
    file.close()

def send_mail(recipient, subject, body):
    import smtplib

    FROM = user+"@physik.fu-berlin.de"
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    print(user,pwd)
    print(message)
    try:
        server = smtplib.SMTP("mail.zedat.fu-berlin.de", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        pass
    except:
        print "Failed to send mail."

print("Type username and password for Zedat Mail authentification.")
user = raw_input("username: ")
pwd = getpass.getpass()
print("Try every 30s if reservation is available and send a mail to all recipients\
in the recipients.dat file.")

URL = "http://www.cinestar.de/de/kino/berlin-cinestar-original-im-sony-center/veranstaltungen/original-sneak-mysterie-movie-ov/"

while True:
    htmlSource = read_url(URL)
    if htmlSource.find("503 Service Temporarily Unavailable") != -1:
        time.sleep(30)
    else: break


if htmlSource.find(">20:00</time>") != -1:
    subject = "Sneak tickets available!"
    body = "Sneak tickets are available. For buying or reservation go to:\n"+URL+"\n\nBest,\nSneak-Bot"
    recipients = read_recipients()
    send_mail(recipients,subject,body)
