import os
import logging
import MySQLdb
import time
import requests
import datetime
import xml.etree.ElementTree as ET

#Connect to MySQL Database
db = MySQLdb.connect(host="localhost", user="root", passwd="ccmpProject**", db="chaupal",charset='utf8')
cur=db.cursor()
db.autocommit(True)
#Query to set up Database to read Hindi Characters
query="SET NAMES utf8"
cur.execute(query)


today = datetime.date.today()
todaystring=today.strftime('%Y%m%d')
xmldir="/home/libtech/libtechweb/chattisgarh/chaupalrsync/xml"
for file in os.listdir(xmldir):
  if ((file.endswith(".xml")) ):
    ts=file.split("_")[2].split(".")[0]
    xmlname=xmldir+"/"+file
    r=open(xmlname,'r').read()
    root = ET.fromstring(r)
    for entity in root.findall('newJobcardApplication'):
      block = entity.find('block').text
      panchayat = entity.find('panchayat').text
      applicantName = entity.find('applicantName').text
      relationName = entity.find('relationName').text
      applicationDate = entity.find('applicationDate').text
      print applicationDate
      query="insert into jobcardApplications (ts,block,panchayat,applicantName,relationName,applicationDate) values ("+ts+",'"+block+"','"+panchayat+"','"+applicantName+"','"+relationName+"','"+applicationDate+"');"
      try:
        cur.execute(query)
      except MySQLdb.IntegrityError,e:
        errormessage=(time.strftime("%d/%m/%Y %H:%M:%S "))+str(e)+"\n"
        continue
