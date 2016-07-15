"""
Created on 15 Jan 2015
@description: notify subscribed users when new packages are ready for download
@author: Pinaki Chandrasekhar
@modified:  Tim Cavanagh	21/10/2015  Notify email details.
            Tim Cavanagh    04/03/2016  Added extra param to handle exception notification
"""

import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config


def notifysubscribers(filelist, msg):
    sender = config.email_sender
    # emails = list()
    # f = open(config.email_subscribers, 'r')
    # for line in f:
    #     line = line.strip()
    #     emails.append(line)
    # f.close()
    emails = config.email_subscribers

    html1 = """\
    <html>
      <head></head>
      <body>
        <p>Hello,<br>
           The following AdelaideX data packages/files are available for download from the Asset Share:<br> 
           <ol>"""
    errmsg = ''
    if msg:
        errmsg = "<h3>An error has occurred.</h3>" + msg + "<br/>"
    html2 = ""
    for f in filelist:
        if 'database-data' in f:
            html2 = html2 + "<li>" + "DataPackages/decrypted/" + f[len(
                config.package_path + "/unzipped/"):f.find('.gpg')] + "</li>"
        else:
            html2 = html2 + "<li>" + "DataPackages/decrypted/" + f[len(config.package_path + "/"):f.find(
                ".gpg")] + "</li>"
    html3 = """\
            </ol>    
        </p>
        Cheers Tim<br><br>
        --<br> 
        Tim Cavanagh<br>
        AdelaideX Data Czar<br>
	    Technology Services<br>
	    P:  8316 6407<br>
	    M:  0434 079 402<br>
	    E: tim.cavanagh@adelaide.edu.au<br>
        The University of Adelaide,<br>
		AUSTRALIA 5005<br>
        </body>
    </html>"""
    html = html1 + errmsg + html2 + html3
    subject = 'AdelaideX Data Packages Update: ' + str(datetime.datetime.now())
    for to in emails:
        sendMail(subject, sender, to, html)


def sendMail(subject, frm, to, body):
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = frm
    msg['To'] = to

    part2 = MIMEText(body, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    #  msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    s = smtplib.SMTP('localhost')
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.

    s.sendmail(msg[frm], msg['To'], msg.as_string())
    s.quit()
