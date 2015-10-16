import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import time
import re
import os
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
from settings import dbhost,dbuser,dbpasswd,sid,token
from globalSettings import datadir
#Error File Defination
errorfile = open('/tmp/processFTO.log', 'a')
#File Path where all the Downloaded FTOs would be placed
districtName="SURGUJA"
ftofilepath=datadir+"/CHATTISGARH/"+districtName+"/"
#Connect to MySQL Database
db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, db="surguja",charset='utf8')
cur=db.cursor()
db.autocommit(True)
#Query to set up Database to read Hindi Characters
query="SET NAMES utf8"
cur.execute(query)

#Query to get the FTO
query=" select f.id,f.ftoNo,b.name,f.finyear from ftoDetails f,blocks b where b.blockCode=f.blockCode and b.isActive=1 and f.finyear='16' and f.isDownloaded=1 and f.isProcessed=0 "
cur.execute(query)
if cur.rowcount:
  results = cur.fetchall()
  for row in results:
    ftoid=row[0]
    ftoNo=row[1]
    blockName=row[2]
    finyear=row[3]
    print str(ftoid)+"  "+finyear+"  "+ftoNo+"  "+blockName
    if finyear=='16':
      fullfinyear='2015-2016'
    elif finyear=='15':
      fullfinyear='2014-2015'
    else:
      fullfinyear='2013-2014'
    ftofilename=ftofilepath+blockName+"/FTO/"+fullfinyear+"/"+ftoNo+".html"
    print ftofilename
    if (os.path.isfile(ftofilename)): 
      ftohtml=open(ftofilename,'r').read()
    else:
      ftohtml="Timeout expired"
    if "Timeout expired" in ftohtml:
      print "This is time out expired file"
      errorflag=1
      query="update ftoDetails set isDownloaded=0 where id="+str(ftoid)
      cur.execute(query)
    else:
      htmlsoup=BeautifulSoup(ftohtml)
      try:
        table=htmlsoup.find('table',align="center")
        rows = table.findAll('tr')
        errorflag=0
      except:
        errorflag=1
        query="update ftoDetails set isDownloaded=0 where id="+str(ftoid)
        cur.execute(query)
 
    if errorflag==0:
      for tr in rows:
        cols = tr.findAll('td')
        tdtext=''
        block= cols[1].string.strip()
        if blockName==block.upper():
          srno= cols[0].string.strip()
          jobcardpanchayat="".join(cols[2].text.split())
          referenceNo="".join(cols[3].text.split())
          transactiondatestring="".join(cols[4].text.split())
          applicantName="".join(cols[5].text.split())
          wagelistNo="".join(cols[6].text.split())
          primaryAccountHolder="".join(cols[7].text.split())
          accountNo="".join(cols[8].text.split())
          bankCode="".join(cols[9].text.split())
          IFSCCode="".join(cols[10].text.split())
          amounttobecredited="".join(cols[11].text.split())
          creditedAmount="".join(cols[12].text.split())
          status="".join(cols[13].text.split())
          processeddatestring="".join(cols[14].text.split())
          bankprocessdatestring="".join(cols[15].text.split())
          utrNo="".join(cols[16].text.split())
          rejectionReason="".join(cols[17].text.split())
          panchayat=jobcardpanchayat[jobcardpanchayat.index("(") + 1:jobcardpanchayat.rindex(")")]
          jobcard=jobcardpanchayat[0:jobcardpanchayat.index("(")]
          #print panchayat+"  "+jobcard
          if transactiondatestring != '':
            transactiondate = time.strptime(transactiondatestring, '%d/%m/%Y')
            transactiondate = time.strftime('%Y-%m-%d %H:%M:%S', transactiondate)
          else:
            transactiondate=''
          if processeddatestring != '':
            processeddate = time.strptime(processeddatestring, '%d/%m/%Y')
            processeddate = time.strftime('%Y-%m-%d %H:%M:%S', processeddate)
          else:
      			processeddate=''
          if bankprocessdatestring != '':
            bankprocessdate = time.strptime(bankprocessdatestring, '%d/%m/%Y')
            bankprocessdate = time.strftime('%Y-%m-%d %H:%M:%S', bankprocessdate)
          else:
            bankprocessdate=''
          print ftoNo+"  "+jobcard+"  "+panchayat 
          query="insert into ftoTransactionDetails (ftoNo,referenceNo,jobcard,applicantName,primaryAccountHolder,accountNo,wagelistNo,transactionDate,processedDate,status,rejectionReason,utrNo,creditedAmount,bankCode,IFSCCode) values ('"+ftoNo+"','"+referenceNo+"','"+jobcard+"','"+applicantName+"','"+primaryAccountHolder+"','"+accountNo+"','"+wagelistNo+"','"+transactiondate+"','"+processeddate+"','"+status+"','"+rejectionReason+"','"+utrNo+"',"+str(creditedAmount)+",'"+bankCode+"','"+IFSCCode+"');"
          #print query
          try:
            cur.execute(query)
          except MySQLdb.IntegrityError,e:
            errormessage=(time.strftime("%d/%m/%Y %H:%M:%S "))+str(e)+"\n"
            errorfile.write(errormessage)
            continue
      query="update ftoDetails set isProcessed=1 where id="+str(ftoid);
    #print query
      cur.execute(query)
