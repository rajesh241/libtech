import os

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def arrayToHTMLLine(tableArray):
  htmlLine="<tr>"
  for a in tableArray:
    htmlLine+="<td>"+str(a)+"</td>"
  htmlLine+="</tr>"
  return htmlLine
def libtechSendMail(sender,receiver,subject,messagehtml):
  
  # Create message container - the correct MIME type is multipart/alternative.
  msg = MIMEMultipart('alternative')
  msg['Subject'] = subject 
  msg['From'] = sender
  msg['To'] = receiver
  
  # Create the body of the message (a plain-text and an HTML version).
  text = "It seems you are not able to see html messages"
  
  # Record the MIME types of both parts - text/plain and text/html.
  part1 = MIMEText(text, 'plain')
  part2 = MIMEText(messagehtml, 'html')
  
  # Attach parts into message container.
  # According to RFC 2046, the last part of a multipart message, in this case
  # the HTML message, is best and preferred.
  msg.attach(part1)
  msg.attach(part2)
  
  # Send the message via local SMTP server.
  s = smtplib.SMTP('localhost')
  # sendmail function takes 3 arguments: sender's address, recipient's address
  # and message to send - here it is sent as one string.
  s.sendmail(sender, receiver, msg.as_string())
  s.quit()
def genBroadcastReport(cur,bid,name):
  s="The bid for Broadcast is"+str(bid)
  print s
  reportFile=open("/home/libtech/libtechweb/reports/broadcasts/"+str(bid)+"_"+name+".csv",'w')
  oneline="phone,status,atempts,duration,callTime\n"
  reportFile.write(oneline)
  query="select cc.ctime,cs.phone,cc.duration,cs.attempts from callStatus cs,CompletedCalls cc where cs.success=1 and cc.success=1 and cc.bid=cs.bid and cc.phone=cs.phone and cs.bid="+str(bid)
  cur.execute(query)
  results = cur.fetchall()
  status="success"
  for row in results:
    ctime=row[0]
    phone=row[1]
    duration=row[2]
    attempts=row[3]
    oneline=phone+","+status+","+str(attempts)+","+str(duration)+","+str(ctime)+"\n"
    #print oneline
    reportFile.write(oneline)
  status="expired"
  query="select phone,attempts from callStatus where expired=1 and bid="+str(bid)
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    phone=row[0]
    attempts=row[1] 
    oneline=phone+","+status+","+str(attempts)+",,"+"\n"
    #print oneline
    reportFile.write(oneline)
  status="MaxRetryReached"
  query="select phone,attempts from callStatus where maxRetryFail=1 and bid="+str(bid)
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    phone=row[0]
    attempts=row[1] 
    oneline=phone+","+status+","+str(attempts)+",,"+"\n"
    reportFile.write(oneline)
    #print oneline
