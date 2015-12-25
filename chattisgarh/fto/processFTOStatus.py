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
query=" select f.id,f.ftoNo,b.name,f.finyear,f.blockCode from ftoDetails f,blocks b where b.blockCode=f.blockCode and b.isActive=1 and f.finyear='16' and f.isProcessed=1 and f.isStatusDownloaded=1 and f.isStatusProcessed=0 and f.incorrectPOFile!=1 "
#query=" select f.id,f.ftoNo,b.name,f.finyear,f.blockCode from ftoDetails f,blocks b where b.blockCode=f.blockCode and b.isActive=1 and f.finyear='16' and f.isStatusDownloaded=1 and f.isStatusProcessed=0 and ftoNo='CH3305003_081015FTO_142597'"
cur.execute(query)
if cur.rowcount:
  results = cur.fetchall()
  for row in results:
    ftoid=str(row[0])
    ftoNo=row[1]
    blockName=row[2]
    finyear=row[3]
    blockCode=row[4]

    print str(ftoid)+"  "+finyear+"  "+ftoNo+"  "+blockName
    if finyear=='16':
      fullfinyear='2015-2016'
    elif finyear=='15':
      fullfinyear='2014-2015'
    else:
      fullfinyear='2013-2014'
    ftofilename=ftofilepath+blockName+"/FTO/"+fullfinyear+"/"+ftoNo+"_status.html"
    print ftofilename
    if (os.path.isfile(ftofilename)): 
      ftohtml=open(ftofilename,'r').read()
      if "The file name does not appear to be correct" in ftohtml:
        print "This does not seem like a postoffice PO"
        errorflag=1
      else:
        htmlsoup=BeautifulSoup(ftohtml)
        try:
          table=htmlsoup.find('table',id="ctl00_ContentPlaceHolder1_Table1")
          rows = table.findAll('tr')
          errorflag=0
        except:
          errorflag=1
      print "errorflag is "+str(errorflag)
   
      if errorflag==0:
        for tr in rows:
          cols = tr.findAll('td')
          tdtext=''
          eventDate= cols[0].text
          if eventDate != 'Date Time':
            print eventDate
            event = cols[1].text
            office= cols[2].text
            fileid=cols[3].text
            print eventDate+event+office+fileid
            eventDateFormat='%d %M %Y %H:%i:%s'
            query="insert into ftoStatus (ftoNo,blockCode,finyear,eventDate,event,office,fileid) values ('%s','%s','%s',STR_TO_DATE('%s','%s'),'%s','%s','%s');" % (ftoNo,blockCode,finyear,eventDate,eventDateFormat,event,office,fileid)
            
            print query
            cur.execute(query)
        query="update ftoDetails set isStatusProcessed=1 where id=%s" %(ftoid)
        cur.execute(query)
      else:
        query="update ftoDetails set incorrectPOFile=1 where id=%s" %(ftoid)
        cur.execute(query)
