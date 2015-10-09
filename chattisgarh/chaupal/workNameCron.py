import os
import logging
import MySQLdb
import time
import requests
import datetime
import xml.etree.ElementTree as ET
import re
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
import libtechFunctions
import globalSettings
import settings
from settings import dbhost,dbuser,dbpasswd,sid,token
from libtechFunctions import getjcNumber,singleRowQuery,getBlockCodeFromJobcard,getPanchayatCodeFromJobcard,getBlockName,getPanchayatName,addPhoneAddressBook

def main():
  print 'Content-type: text/html'
  print 
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use surguja"
  cur.execute(query)
  query="select stateCode,districtCode,blockCode,panchayatCode,workCode,workName,finyear from musters where finyear='16' group by workCode"
#  query="select phone,bid,success,ctime,duration,callparams,vendorcid from CompletedCalls  "
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    stateCode=row[0]
    districtCode=row[1]
    blockCode=row[2]
    panchayatCode=row[3]
    workCode=row[4]
    workName=row[5]
    finyear=row[6]
    query="insert into works (stateCode,districtCode,blockCode,panchayatCode,workCode,workName,finyear) values ('%s','%s','%s','%s','%s','%s','%s') " %(stateCode,districtCode,blockCode,panchayatCode,workCode,workName,finyear)
    try:
      cur.execute(query)
    except MySQLdb.IntegrityError,e:
      errormessage=(time.strftime("%d/%m/%Y %H:%M:%S "))+str(e)+"\n"
      continue
             
if __name__ == '__main__':
  main()
