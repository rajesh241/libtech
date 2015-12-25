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
  query="select bid,phone,callid from callSummary where status='pending' and bid<300 "
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    bid=str(row[0])
    phone=row[1]
    callid=str(row[2])
    print callid+"  "+bid+"   "+phone
    query="select count(*) from CompletedCalls where bid=%s and phone='%s'" %(bid,phone)
    cur.execute(query)
    row1 = cur.fetchone()
    attempts=str(row1[0])
    query="select success from CompletedCalls where bid=%s and phone='%s' and (success=1 or success=2)" % (bid,phone)
    success=singleRowQueryV1(cur,query)
    status='expired'
    if(success  == 1):
      status='success'
    elif (success ==2):
      status='failedMaxRetry'
    duration='0'
    ctime=''
    sid=''
    vendor=''
    query="select ctime,duration,vendorcid,vid from CompletedCalls where bid=%s and phone='%s' and success=1" % (bid,phone)
    cur.execute(query)
    if(cur.rowcount >= 1):
      row3 = cur.fetchone()
      duration=str(row3[1])
      ctime=row3[0]
      sid=row3[2]
      vid=row3[3]
      vendor='tringo'
      if(vid == 1):
        vendor='awazde'
    query="update callSummary set attempts=%s,vendor='%s',duration=%s,status='%s',callStartTime='%s',sid='%s' where callid=%s " % (attempts,vendor,str(duration),status,ctime,sid,callid)
    print query
    cur.execute(query)

if __name__ == '__main__':
  main()
