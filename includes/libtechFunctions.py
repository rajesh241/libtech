import os
import csv
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def gethtmlheader():
  myhtml="""
    <html>
     <head>
     <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
     <style>
    table, th, td {
    border: 2px solid #613318;
    border-collapse: collapse;
    }
    td,th {
     padding-left:5px;
     padding-right:5px;
     padding-top:2px;
     padding-bottom:2px;
}
    .tdwhite{
    background=#FF0000;
}
   th{
    background-color:  #855723;
     color: #FFFFFF;
}
    table {
     margin-bottom: 20px
   }
     a{
       color:#8F3B1B

    </style>
    </head>
     <body>"""
  return myhtml
def gethtmlfooter():
  myhtml="""
    </body></html>
"""
  return myhtml

def singleRowQuery(cur,query):
  cur.execute(query)
  result=cur.fetchone()
  return result[0]

def getcountquery(cur,query):
  cur.execute(query)
  countrow=cur.fetchone()
  return countrow[0]

def writecsv(cur,query,filename):
  f=open(filename,"w");
  writer = csv.writer(f)
  cur.execute(query)
  headerlist=[];
  #writer.writerow( ('Block', 'Panchayat', 'jobcard','HeadOfFamily','Caste','Issue Date','Village','Applicant No','Applicant Name', 'Age','Gender','Account No','Bank Name') )
  for header in cur.description:
    headerlist.append(header[0])
  writer.writerow(headerlist)
  results = cur.fetchall()
  for row in results:
    writer.writerow(row) 
  f.close()
 # print str(cur.description())

def gen2colOptions(inputlabel,inputname,optionArray,curvalue):
  myhtml=""
  myhtml+="<tr><td>"+inputlabel+"</td>"
  myhtml+='<td><select name="'+inputname+'">'
  count=0
  while (count < len(optionArray)):
    curoption=optionArray[count]
    optionvalue='<option value="'+curoption+'" >'+curoption+' </option>'
    if(curoption == curvalue):
      optionvalue='<option value="'+curoption+'" selected >'+curoption+' </option>'
    myhtml+=optionvalue
    count = count+1
  myhtml+="</td></tr>"
  return myhtml
def gen2colTable(headers,headerfixed,values):
  myhtml="";
  maxrow=len(headers)
  count=0
  while (count < len(headers)):
    curvalue=getstring(values[count])
    if(headerfixed[count] == 0):
      curvalue='<input type="text" size="100" value="'+curvalue+'"></input>'
    myhtml+="<tr><td>"+headers[count]+"</td><td>"+curvalue+"</td></tr>"
    count = count +1
  return myhtml

    
def arrayToHTMLLineTh(tableArray):
  htmlLine="<tr>"
  for a in tableArray:
    htmlLine+="<th>"+str(a)+"</th>"
  htmlLine+="</tr>"
  return htmlLine

def getstring(a):
  if isinstance(a, basestring):
    return a
  else:
    return str(a)
 
def arrayToHTMLLine(tdtype,tableArray):
  htmlLine="<tr>"
  i =0
  for a in tableArray:
    if(i ==0 ):
      i =1
      tdclass='#FFFFFF'
    else:
      i=0
      tdclass='#B99C6B'
    if isinstance(a, basestring):
      htmlLine+='<'+tdtype+' bgcolor="'+tdclass+'">'+a+'</'+tdtype+'>'
    else:
      htmlLine+='<'+tdtype+'  bgcolor="'+tdclass+'">'+str(a)+'</'+tdtype+'>'
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
