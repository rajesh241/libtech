import os
import logging
import MySQLdb
import time
import requests
import datetime
import xml.etree.ElementTree as ET
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
import libtechFunctions
import globalSettings
from libtechFunctions import gethtmlheader 
from libtechFunctions import gethtmlfooter 
from libtechFunctions import singleRowQuery,arrayToHTMLLine,writecsv 
from globalSettings import broadcastsReportFile,broadcastReportFilePath


#Connect to MySQL Database
db = MySQLdb.connect(host="localhost", user="root", passwd="ccmpProject**", db="libtech",charset='utf8')
cur=db.cursor()
db.autocommit(True)
#Query to set up Database to read Hindi Characters
query="SET NAMES utf8"
cur.execute(query)


today = datetime.date.today()
todaystring=today.strftime('%Y%m%d')
xmltype="addressbookEntry"
xmldir="/home/libtech/libtechweb/chattisgarh/chaupalrsync/xml"
i=0
for file in os.listdir(xmldir):
  #if ((file.endswith(".xml")) and (todaystring in file) and (xmltype in file)):
  if ((file.endswith(".xml")) and (xmltype in file)):
    i = i +1
    print "The value of i  is "+str(i)
#  if ((file.endswith(".xmt"))  ):
    ts=file.split("_")[2].split(".")[0]
    xmlname=xmldir+"/"+file
    print xmlname
    r=open(xmlname,'r').read()
    root = ET.fromstring(r)
    for entity in root.findall('addressbookEntry'):
      block = entity.find('block').text
      panchayat = entity.find('panchayat').text
      jobcard = entity.find('jobcard').text
      phone = entity.find('phone').text
      if (phone is not None):
        query="select count(*) from addressbook where phone='"+phone+"';"
        print query
        count=singleRowQuery(cur,query)
        if (count == 0):
          query="insert into addressbook (phone) values ('"+phone+"');"
          print query
          cur.execute(query)
        query ="update addressbook set district='surguja',block='"+block+"',panchayat='"+panchayat+"' where phone='"+phone+"';"
       # query="insert into addressbook (region,district,block,panchayat,jobcard,phone) values ('chaupal','surguja','"+block+"','"+panchayat+"','"+jobcard+"','"+phone+"');"
        print query
        try:
          cur.execute(query)
        except MySQLdb.IntegrityError,e:
          errormessage=(time.strftime("%d/%m/%Y %H:%M:%S "))+str(e)+"\n"
          continue
