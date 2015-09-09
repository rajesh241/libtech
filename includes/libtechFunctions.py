import os
import csv
import smtplib
import MySQLdb

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import re
import string	
import requests
import xml.etree.ElementTree as ET

import settings
from settings import dbhost,dbuser,dbpasswd,sid,token
def getOnlyDigits(s):
  all=string.maketrans('','')
  nodigs=all.translate(all, string.digits)
  return s.translate(all, nodigs)

def getNumberString(a):
  thousands=int(a)/1000
  thousandsReminder=int(a) % 1000
  hundreds=thousandsReminder / 100
  tens=thousandsReminder % 100
  numberString=''
  if thousands > 0:
    numberString+= str(thousands*1000)+","
  if hundreds > 0:
    numberString+=str(hundreds*100)+","
  if tens>0:
    numberString+=str(tens)
  return numberString.rstrip(',')
def getjcNumber(jobcard):
  jobcardArray=jobcard.split('/')
#  print jobcardArray[1]
  jcNumber=re.sub("[^0-9]", "", jobcardArray[1])
  return jcNumber


def gmailSendMail(recipient,subject,body):
  # The below code never changes, though obviously those variables need values.
  session = smtplib.SMTP('smtp.gmail.com', 587)
  session.ehlo()
  session.starttls()
  session.login(GMAIL_USERNAME, GMAIL_PASSWORD)
  headers = "\r\n".join(["from: " + GMAIL_USERNAME,
                       "subject: " + subject,
                       "to: " + recipient,
                       "mime-version: 1.0",
                       "content-type: text/html"])

  # body_of_email can be plaintext or html!                    
  content = headers + "\r\n\r\n" + body
  session.sendmail(GMAIL_USERNAME, recipient, content)


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
def singleRowQueryV1(cur,query):
  cur.execute(query)
  if (cur.rowcount == 0):
    return "ERROR"
  else:
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

def getBlockName(cur,blockCode):
  query="select surguja.blocks.name from surguja.blocks where surguja.blocks.blockCode='%s'" % blockCode
  return singleRowQuery(cur,query)
def getPanchayatName(cur,blockCode,panchayatCode):
  query="select surguja.panchayats.name from surguja.panchayats where surguja.panchayats.blockCode='%s' and surguja.panchayats.panchayatCode='%s'" % (blockCode,panchayatCode)
  return singleRowQuery(cur,query)

def addPhoneAddressBook(cur,phone,district,block,panchayat):
  if(len(phone) == 10):
    query="select id from addressbook where phone='"+phone+"'"
    cur.execute(query)
    if (cur.rowcount == 0):
      query="insert into addressbook (district,block,panchayat,phone) values ('%s','%s','%s','%s');" %(district.lower(),block.lower(),panchayat.lower(),phone)
    else:
      query="update addressbook set district='%s',block='%s',panchayat='%s' where phone='%s'" %(district.lower(),block.lower(),panchayat.lower(),phone)
    cur.execute(query)
    return 'success'
  else:
    return 'fail'
  
def deletePhoneAddressBook(cur,phone):
  query="delete from addressbook where phone='%s'" % phone
  cur.execute(query)
  query="delete from jobcardPhone where phone='%s'" % phone
  cur.execute(query)
  query="insert into addressbook (phone) value ('%s')" % phone
  cur.execute(query)
def addJobcardPhone(cur,phone,jobcard):
  if(len(phone) == 10):
    blockCode=jobcard[6:9]
    panchayatCode=jobcard[10:13]
    blockName=getBlockName(cur,blockCode)
    panchayatName=getPanchayatName(cur,blockCode,panchayatCode)
    addPhoneAddressBook(cur,phone,'surguja',blockName,panchayatName)
    if (jobcard != "NoJobCard"):
      query="select id from jobcardPhone where jobcard='"+jobcard+"'"
      #myhtml+= '<br />' + getCenterAligned('<h5 style="color:red"> %s</h5>' % query )
      cur.execute(query)
      if (cur.rowcount == 0):
        query="insert into jobcardPhone (jobcard,phone) values ('%s','%s')" % (jobcard,phone)
      else:
        query="update jobcardPhone set phone='%s' where jobcard='%s'" %(phone,jobcard)
     # myhtml+= '<br />' + getCenterAligned('<h5 style="color:red"> %s</h5>' % query )
      cur.execute(query)
    return "success"
  else:
    return "fail"

def checkDND(phone):
  url = 'https://%s:%s@twilix.exotel.in/v1/Accounts/%s/Numbers/%s' % (sid, token, sid, phone)
  r = requests.get(url)
  #print r.content
  root = ET.fromstring(r.content)
  for number in root.findall('Numbers'):
    PhoneNumber = number.find('PhoneNumber').text
    Circle = number.find('Circle').text
    CircleName = number.find('CircleName').text
    Type = number.find('Type').text
    Operator = number.find('Operator').text
    OperatorName = number.find('OperatorName').text
    DND = number.find('DND').text
    if Circle is  None:
      Circle='00'
    if OperatorName is  None:
      OperatorName='unknown'
  
    if (Circle == "AP"):
      exophone="04030911001"
    elif (Circle =="MH"):
      exophone="02233814264"
    elif (Circle =="MU"):
      exophone="02233814264"
    else:
      exophone="08033545179"
  return DND.lower(),exophone 
  
def checkLocalDND(cur,phone):
  query="use libtech"
  cur.execute(query)
  query="select dnd,exophone from addressbook where phone='%s'" % phone
  cur.execute(query)
  if(cur.rowcount == 1):
    row= cur.fetchone()
    return row[0],row[1] 
  else:
    return checkDND(phone)

def gettringoaudio(rawlist):
  tringofilelist=rawlist.rstrip(',')
  tringoArray=tringofilelist.split(',')
  noOfFiles=len(tringoArray)
  i=0
  tringoaudio=''
  while(i<20):
    curFileID='27503'
    if(i < noOfFiles):
      curFileID=tringoArray[i]
    i=i+1
    tringoaudio+="&fileid"+str(i)+"="+curFileID
  return tringoaudio

def getaudio(cur,rawlist):
  error=0
  filelist=rawlist.rstrip(',')
  filelistArray=filelist.split(',')
  audio=''
  for audioFileID in filelistArray:
    query="select count(*) from audioLibrary where id="+audioFileID
    audioExists=singleRowQuery(cur,query)
    if (audioExists == 1):
      query="select filename from audioLibrary where id="+audioFileID
#      print query
      audio+=singleRowQuery(cur,query)
    else:
      error=1
    audio+=','
  audio=audio.rstrip(',')
  return audio,error


def scheduleTransactionCall(cur,bid,phone):
  query="select bid,type,minhour,maxhour,tfileid,fileid,groups,vendor,district,blocks,panchayats,priority from broadcasts where bid=%s;" % bid
  cur.execute(query)
  row= cur.fetchone()
  bid=str(row[0])
  minhour=str(row[2])
  maxhour=str(row[3])
  tringoaudio=gettringoaudio(row[4])
  audio,error=getaudio(cur,row[5])
  requestedVendor=row[7]
  priority=row[11]
  broadcastType=row[1]
  dnd,exophone=checkDND(phone)
  print dnd+exophone
  if (error == 0):
    skip=0
    if(dnd == 'yes'):
      if( (requestedVendor == "any") or (requestedVendor =="tringo")):
        vendor='tringo'
      else:
        vendor="any"
        skip=1 
    else:
      vendor=requestedVendor;
    print "phone "+phone+" skip"+str(skip)+"vendor "+vendor
    if len(phone) == 10 and phone.isdigit() and skip == 0:
      query="insert into callQueue (priority,vendor,bid,minhour,maxhour,phone,audio,tringoaudio,exophone) values ("+str(priority)+",'"+vendor+"',"+bid+","+minhour+","+maxhour+",'"+phone+"','"+audio+"','"+tringoaudio+"','"+exophone+"');"
     # print query
      cur.execute(query)
      query="insert into callStatus (bid,phone) values ("+bid+",'"+phone+"');"
     # print query
      cur.execute(query)
  
def getBlockCodeFromJobcard(jobcard):
  return  jobcard[6:9]
def getPanchayatCodeFromJobcard(jobcard):
  return jobcard[10:13]

def getWageBroadcastAudioArray(cur,jobcard):
  query="use surguja"
  cur.execute(query)
  query="select mt.totalWage,DATE_FORMAT(mt.creditedDate,'%Y'),DATE_FORMAT(mt.creditedDate,'%M'),DATE_FORMAT(mt.creditedDate,'%d'),p.name,mt.id from musterTransactionDetails mt,panchayats p where mt.blockCode=p.blockCode and mt.panchayatCode=p.panchayatCode and mt.jobcard='"+jobcard+"' order by mt.creditedDate desc limit 1;"
  cur.execute(query)
  if (cur.rowcount == 0):
    return "error"
  else:
    row=cur.fetchone()
    amount=getNumberString(row[0])
    date=str(row[3])+","+str(row[2].lower())+","+str(row[1])
    panchayat=row[4].lower()
    jobcardNo=getNumberString(getOnlyDigits(getjcNumber(jobcard)))
   # date="25,aug"
   # panchayat="lundra"
    baseMessage="chattisgarh_wage_broadcast_static0,panchayat,chattisgarh_wage_broadcast_static1,jobcard,chattisgarh_wage_broadcast_static2,amount,chattisgarh_wage_broadcast_static3,date,chattisgarh_wage_broadcast_static4"
    baseMessage=baseMessage.replace('jobcard',jobcardNo)
    baseMessage=baseMessage.replace('date',date)
    baseMessage=baseMessage.replace('amount',amount)
    baseMessage=baseMessage.replace('panchayat',panchayat)
    audioMessage=baseMessage+",chattisgarh_wage_broadcast_repeat,"+baseMessage+",chattisgarh_wage_broadcast_thankyou"
    print audioMessage
    #print audioMessage
    return audioMessage

def scheduleWageBroadcastCall(cur,jobcard,phone):
  dnd,exophone=checkLocalDND(cur,phone)
  print dnd+exophone
  if (dnd == 'no'):
    audio=getWageBroadcastAudioArray(cur,jobcard)
    if (audio == "error"):
      print "There is some error here"
    else:
      query="use libtech" 
      cur.execute(query)
      query="insert into callQueue (template,priority,vendor,bid,minhour,maxhour,phone,audio,exophone) values ('wageBroadcast',1,'exotel',1185,7,21,'%s','%s','%s');" %(phone,audio,exophone)
      cur.execute(query)
      query="insert into callStatus (bid,phone) values (1185,'"+phone+"');"
      cur.execute(query)
