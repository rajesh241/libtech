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
from libtechFunctions import getjcNumber,singleRowQueryV1,getBlockCodeFromJobcard,getPanchayatCodeFromJobcard,getBlockName,getPanchayatName,addPhoneAddressBook
def main():
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use libtech"
  cur.execute(query)
  query="select bid,phone,callid from callSummary where bid<300 and callLogsDone=0 "
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    bid=str(row[0])
    phone=row[1]
    callid=str(row[2])
    print callid+"  "+bid+"   "+phone

    query="select callparams,ctime,vendorcid,duration,status,vid from CompletedCalls where bid=%s and phone='%s' order by ccid" % (bid, phone)

    cur.execute(query)
    results5 = cur.fetchall()
    retry=0
    for row5 in results5:
      retry=retry+1
      callparams=row5[0]
      ctime=row5[1]
      vendorcid=row5[2]
      duration=str(row5[3])
      success=row5[4]
      vid=row5[5]
      vendor='tringo'
      if(vid == 1):
        vendor='awazde'
      if(success == 3):
        status='error'
      elif(success == 1):
        status='pass'
      else:
        status='fail'
      query="insert into callLogs (callid,retry,bid,vendor,phone,sid,callStartTime,duration,status,audio) values (%s,%s,%s,'%s','%s','%s','%s','%s','%s','%s')" % (str(callid),str(retry),bid,vendor,phone,vendorcid,ctime,duration,status,callparams)
      cur.execute(query)
    query="update callSummary set callLogsDone=1 where callid=%s" % callid
    cur.execute(query)


if __name__ == '__main__':
  main()
