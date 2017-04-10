#This code will get the Oabcgatat Banes
import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import time
import re
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
#This is a Kludge to remove all the input tags from the html because for some reason Beautiful Soup does not parse the html correctly
#regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
regex=re.compile(r'<input type="hidden" value="[A-Za-z0-9]+.*?"\s*/>+',re.DOTALL)
#Getting the block name as parameter
inblock=sys.argv[1]
print inblock
#Error File Defination
errorfile = open('/home/goli/libtech/logs/processJobcards_'+inblock+'.log', 'a')
exceptionfile = open('/home/goli/libtech/logs/exceptions/jobcardException_'+inblock+'.csv', 'a')
debugfile=open('/tmp/debug.html','w')
#File Path where all the Downloaded FTOs would be placed
districtName="SURGUJA"
jcfilepath="/home/goli/libtech/data/CHATTISGARH/"+districtName+"/"
#Connect to MySQL Database
db = MySQLdb.connect(host="localhost", user="root", passwd="golani123", db="surguja",charset='utf8')
cur=db.cursor()
db.autocommit(True)
#Query to set up Database to read Hindi Characters
query="SET NAMES utf8"
cur.execute(query)
#Defining Array of Jobcard Details
jobcardDetails=['header','header','jobcard','headOfFamily','photo','FatherName','Caste','IssueDate','address','village','panchayat','block','district','isBPL']
query="select id,jobcard,stateCode,districtCode,panchayatCode from jobcardRegister where isDownloaded=1 ;"
query="select j.id,j.jobcard,j.stateCode,j.districtCode,j.blockCode,j.panchayatCode,b.name,p.name from jobcardRegister j,blocks b,panchayats p where j.isDownloaded=1 and j.isProcessed=0 and b.blockCode=j.blockCode and p.blockCode=j.blockCode and p.panchayatCode=j.panchayatCode and j.blockcode='"+inblock+"';"
#query="select j.id,j.jobcard,j.stateCode,j.districtCode,j.blockCode,j.panchayatCode,b.name,p.name from jobcardRegister j,blocks b,panchayats p where  j.isProcessed=0 and b.blockCode=j.blockCode and p.blockCode=j.blockCode and p.panchayatCode=j.panchayatCode and j.id=111389;"
print query
cur.execute(query)
if cur.rowcount:
  results = cur.fetchall()
  for row in results:
    jobcardid=row[0]
    jobcard=row[1]
    stateCode=row[2]
    districtCode=row[3]
    blockCode=row[4]
    panchayatCode=row[5]
    blockName=row[6]
    panchayatName=row[7]
    print str(jobcardid) + "  "+jobcard+"  "+blockName +"  "+panchayatName
    jcfilename=jcfilepath+blockName+"/"+panchayatName.upper()+"/jobcardRegister/"+jobcard.replace("/","_")+".html"
    jchtml=open(jcfilename,'r').read()
    if "Timeout expired" in jchtml:
      print "This is time out expired file"
      errorflag=1
      query="update jobcardRegister set isDownloaded=0 where id="+str(jobcardid)
      cur.execute(query)
    elif len(jobcard.split('/')[0])!=17:
      print "The length of Jobcard is not correct"
      errorflag=1
      query="update jobcardRegister set isProcessed=1,jobcardError=1 where id="+str(jobcardid)
      cur.execute(query)
    else:
      jchtml1=re.sub(regex,"",jchtml)#Have to do this else the beautiful soup goofs up. Removes the input tag from HTML
      #debugfile.write(jchtml)
      #jchtml2=open('/tmp/debug2.html','r').read()
      htmlsoup=BeautifulSoup(jchtml)
      try:
        table=htmlsoup.find('table',bgcolor="#FEF3EB")
        rows = table.findAll('tr')
        errorflag=0
      except:
        try:
          htmlsoup=BeautifulSoup(jchtml1)
          table=htmlsoup.find('table',bgcolor="#FEF3EB")
          rows = table.findAll('tr')
          errorflag=0
        except:   
          errorflag=1
          print "Am not able to find the table"
          errormessage=str(jobcardid) + "  "+jobcard+" ERROR  "+blockName +"  "+panchayatName
          #print str(jobcardid) + "  "+jobcard+" ERROR  "+blockName +"  "+panchayatName
          errorfile.write(errormessage)
          query="update jobcardRegister set isDownloaded=0 where id="+str(jobcardid)
          cur.execute(query)
#print(htmlsoup.prettify())
    currow=0
    if errorflag==0:
      for tr in rows:
        cols = tr.findAll('td')
        if len(cols) == 7:
          #print str(currow)+" "+str(len(cols)) 
          col0="".join(cols[0].text.split())
          col1="".join(cols[1].text.split())
          #print col0+col1
        elif len(cols) > 1:
          #print str(currow)+" "+str(len(cols))
          col0="".join(cols[0].text.split())
          col1="".join(cols[1].text.split())
          if currow<14:
            jobcardDetails[currow]=col1
          #print col0+col1
        currow=currow+1
      #print jobcardDetails
      i=0
      for a in jobcardDetails:
        #print str(i)+"  "+a
        i=i+1
      jobcardOnFile=jobcardDetails[2]
      if jobcardOnFile == jobcard:
        #print str(jobcardid) + "  "+jobcard+" Matches  "+blockName +"  "+panchayatName
        headOfFamily=jobcardDetails[3]
        fatherHusbandName=jobcardDetails[5]
        caste=jobcardDetails[6]
        issueDateString=jobcardDetails[7]
        village=jobcardDetails[9]
        isBPL=0
        nameHasError=0
        if jobcardDetails[13] == 'YES':
          isBPL=1 
        #We need to check if the names contain any quotes
        if '\'' in headOfFamily:
          nameHasError=1
          print "The name has Quotes"
          headOfFamily=headOfFamily.replace('\'','\'\'')#We need to replace quotes with double quotes to insert in mysql database
        if '\'' in fatherHusbandName:
          nameHasError=1
          fatherHusbandName=fatherHusbandName.replace('\'','\'\'')#We need to replace quotes with double quotes to insert in mysql database
        #Some Dates on file are in d/m/Y and some dates are m/d/Y so first we need to distinguish that
        if issueDateString != '':
          issueDateParts=re.match(r'(.*)\/(.*)\/(.*)',issueDateString)
          secondpart=issueDateParts.groups()[1]
          #print "Issue date"+issueDateString+"second part "+str(secondpart)
          if int(secondpart) > 12:
            #print "WE enter here if string is greater than 12"
            issueDate = time.strptime(issueDateString, '%m/%d/%Y')
            issueDateError=1
            exceptionmessage="Invaid Date Format,"+jobcard+","+blockName+","+panchayatName+","+issueDateString+"\n"
            exceptionfile.write(exceptionmessage)
          else: 
            issueDate = time.strptime(issueDateString, '%d/%m/%Y')
            issueDateError=0
          issueDate = time.strftime('%Y-%m-%d %H:%M:%S', issueDate)
        else:
          issueDate=''
        #print issueDate
        #Now lets find if the table of workerDetails exists
        try:
          table1=htmlsoup.find('table',id='GridView4')
          rows = table1.findAll('tr')
          workerDetailsAbsent=0
        except:
          print "Worker Details Absent"
          workerDetailsAbsent=1
          errormessage=str(jobcardid) + "  "+jobcard+" Worker Detail Absent  "+blockName +"  "+panchayatName
          #print str(jobcardid) + "  "+jobcard+" ERROR  "+blockName +"  "+panchayatName
          errorfile.write(errormessage)
        query="update jobcardRegister set headOfFamily='"+headOfFamily+"',fatherHusbandName='"+fatherHusbandName+"',caste='"+caste+"',issueDate='"+issueDate+"',isBPL="+str(isBPL)+",workerDetailsAbsent="+str(workerDetailsAbsent)+",nameHasError="+str(nameHasError)+",issueDateError="+str(issueDateError)+",village='"+village+"' where id="+str(jobcardid)
        #print query
        cur.execute(query)
        #This table is for finding worker Details
        if workerDetailsAbsent==0:
          for tr in rows:
            cols = tr.findAll('td')
            if len(cols) > 1:
              applicantNo="".join(cols[0].text.split())
              name="".join(cols[1].text.split())
              gender="".join(cols[2].text.split())
              age="".join(cols[3].text.split())
              accountNo="".join(cols[4].text.split())
              nameHasError=0
              if '\'' in name:
                nameHasError=1
                print "The name has Quotes"
                name=name.replace('\'','\'\'')#We need to replace quotes with double quotes to insert in mysql database
              if not accountNo:
                accountNo=0
              accountNoError=0
              if not str(accountNo).isdigit():
                accountNoError=1
                exceptionmessage="Account No Error,"+jobcard+","+blockName+","+panchayatName+","+str(accountNo)+"\n"
                exceptionfile.write(exceptionmessage)
              bankPOName="".join(cols[5].text.split())
              aadharNo="".join(cols[6].text.split())
              #print applicantNo+"  "+name+"  "+gender+"  "+str(age)+"  "+str(accountNo)+"  "+bankPOName+"  "+str(aadharNo)
              query="insert into jobcardDetails (jobcard,applicantNo,applicantName,gender,age,accountNo,aadharNo,nameHasError,accountNoError) values ('"+jobcard+"',"+str(applicantNo)+",'"+name+" ','"+gender+" ',"+str(age)+",'"+str(accountNo)+"','"+str(aadharNo)+"',"+str(nameHasError)+","+str(accountNoError)+");"
              #print query
              try:
                cur.execute(query)
              except MySQLdb.IntegrityError,e:
                errormessage=(time.strftime("%d/%m/%Y %H:%M:%S "))+str(e)+"\n"
                errorfile.write(errormessage)
              continue
        query="update jobcardRegister set isProcessed=1 where id="+str(jobcardid)
        #print query
        cur.execute(query)
