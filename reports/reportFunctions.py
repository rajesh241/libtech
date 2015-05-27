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
    border: 2px solid #097054;
    border-collapse: collapse;
    }
    table {
     margin-bottom: 20px
   }

    </style>
    </head>
     <body>"""
  return myhtml
def gethtmlfooter():
  myhtml="""
    </body></html>
"""
  return myhtml
def getcountquery(cur,query):
  cur.execute(query)
  countrow=cur.fetchone()
  return countrow[0]

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

def writejobcardcsv(cur,districtCode,districtName,blockCode,panchayatCode,blockName,panchayatName):
  print "writng jobcard csv"
  csvname='/home/libtech/libtechweb/chattisgarh/surguja/'+blockName.lower()+'/jc_csv/'+panchayatName.lower()+'_jobcards.csv'
  htmlname='/home/libtech/libtechweb/chattisgarh/surguja/'+blockName.lower()+'/jc_html/'+panchayatName.lower()+'_jobcards.html'
  htmlnamerejected='/home/libtech/libtechweb/chattisgarh/surguja/'+blockName.lower()+'/jc_html/'+panchayatName.lower()+'_jobcards_rejected_payments.html'
  noAccounthtmlname='/home/libtech/libtechweb/chattisgarh/surguja/'+blockName.lower()+'/jc_html/'+panchayatName.lower()+'_jobcards_noAccount.html'
  print csvname
  myhtml=gethtmlheader()
  myhtml+="<table>"  
  myhtml1=gethtmlheader()
  myhtml1+="<table>"  
 # f=open(csvname,"w");
 # writer = csv.writer(f)
 # writer.writerow( ('Block', 'Panchayat', 'jobcard','HeadOfFamily','Caste','Issue Date','Village','Applicant No','Applicant Name', 'Age','Gender','Account No','Bank Name') )
  tableArray=['Block', 'Panchayat', 'jobcard','HeadOfFamily','Caste','Issue Date','Village','Applicant No','Applicant Name', 'Age','Gender','Account No','Bank Name']
  myhtml+=arrayToHTMLLineTh(tableArray)
  myhtml1+=arrayToHTMLLineTh(tableArray)
  query="select jd.jobcard,j.headOfFamily,j.caste,DATE_FORMAT(j.issueDate,'%d-%M-%Y'),j.village,jd.applicantNo,jd.age,jd.applicantName,jd.gender,jd.accountNo,jd.bankNameOrPOName from jobcardDetails jd,jobcardRegister j where j.jobcard=jd.jobcard and j.blockCode='"+str(blockCode)+"' and j.panchayatCode='"+str(panchayatCode)+"';"
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    jobcard=row[0]
    jobcardlink='<a href="../'+panchayatName.lower()+'/'+jobcard.replace("/","_")+'.html">'+jobcard+'</a>'
    headOfFamily=row[1]
    caste=row[2]
    issueDate=str(row[3])
    village=row[4]
    applicantNo=str(row[5])
    applicantName=row[7]
    age=str(row[6])
    gender=row[8]
    accountNo=str(row[9])
    bankName=str(row[10])
    applicantName
  #  writer.writerow( (blockName, panchayatName, jobcard,headOfFamily,caste,issueDate,village,applicantNo,applicantName,age,gender,accountNo,bankName))
    tableArray=[blockName, panchayatName, jobcardlink,headOfFamily,caste,issueDate,village,applicantNo,applicantName,age,gender,accountNo,bankName]
    myhtml+=arrayToHTMLLine(tableArray)
    if (accountNo == '0'):
      myhtml1+=arrayToHTMLLine(tableArray)
  #f.close()
  myhtml+="</table>"
  myhtml+=gethtmlfooter()  
  myhtml1+="</table>"
  myhtml1+=gethtmlfooter()  
  f=open(htmlname,'w')
  f.write(myhtml.encode("UTF-8"))
  f.close()
  f=open(noAccounthtmlname,'w')
  f.write(myhtml1.encode("UTF-8"))
  f.close()
  #HTML for Failed Jobcards
  myhtml=gethtmlheader()
  myhtml+="<table>"  
  tableArray=['Block', 'Panchayat', 'jobcard','HeadOfFamily','Caste','Issue Date','Village','Muster Fail Transaction','FTO Fail Transaction']
  myhtml+=arrayToHTMLLineTh(tableArray)
  query="select jobcard,headOfFamily,caste,DATE_FORMAT(issueDate,'%d-%M-%Y'),village from jobcardRegister where blockCode='"+str(blockCode)+"' and panchayatCode='"+str(panchayatCode)+"';"
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    jobcard=row[0]
    jobcardlink='<a href="../'+panchayatName.lower()+'/'+jobcard.replace("/","_")+'.html">'+jobcard+'</a>'
    headOfFamily=row[1]
    caste=row[2]
    issueDate=str(row[3])
    village=row[4]
    query="select count(*) c from musterTransactionDetails where jobcard='"+jobcard+"' and (status='Rejected' or status='InvalidAccount')"
    cur.execute(query)
    countrow=cur.fetchone()
    musterfailcount=countrow[0]  
    query="select count(*) c from ftoTransactionDetails where jobcard='"+jobcard+"' and (status='Rejected' or status='InvalidAccount')"
    cur.execute(query)
    countrow=cur.fetchone()  
    ftofailcount=countrow[0] 
    if( (ftofailcount + musterfailcount) > 0):
      tableArray=[blockName, panchayatName, jobcardlink,headOfFamily,caste,issueDate,village,musterfailcount,ftofailcount]
      myhtml+=arrayToHTMLLine(tableArray)
  myhtml+="</table>"
  myhtml+=gethtmlfooter()  
  f=open(htmlnamerejected,'w')
  f.write(myhtml.encode("UTF-8"))
  f.close()
       
     
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
 
def arrayToHTMLLine(tableArray):
  htmlLine="<tr>"
  for a in tableArray:
    if isinstance(a, basestring):
      htmlLine+="<td>"+a+"</td>"
    else:
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
