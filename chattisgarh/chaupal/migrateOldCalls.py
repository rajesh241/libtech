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
from libtechFunctions import getjcNumber,singleRowQueryV1,getBlockCodeFromJobcard,getPanchayatCodeFromJobcard,getBlockName,getPanchayatName,addPhoneAddressBook,getWageBroadcastAudioArray,scheduleWageBroadcastCall
def main():
  print 'Content-type: text/html'
  print 
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use libtech"
  cur.execute(query)
  query="select bid from CompletedCalls where bid>0 group by bid "
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    bid=str(row[0])
    print "Processing BID " +bid
    query="select phone,count(*) from CompletedCalls where bid=%s group by phone" %(bid)
    cur.execute(query)
    results1 = cur.fetchall()
    for row1 in results1:
      phone=row1[0]
      attempts=str(row1[1])
      query="select success from CompletedCalls where bid=%s and phone='%s' and (success=1 or success=2)" % (bid,phone)
      success=singleRowQueryV1(cur,query)
      status='pending'
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
      if(cur.rowcount == 1):
        row3 = cur.fetchone()
        duration=str(row3[1])
        ctime=row3[0]
        sid=row3[2]
        vid=row3[3]
        vendor='tringo'
        if(vid == 1):
          vendor='awazde'
      query="insert into callSummary (bid,attempts,phone,vendor,duration,status,callStartTime,sid) values (%s,%s,'%s','%s',%s,'%s','%s','%s')" % ( bid,str(attempts),phone,vendor,duration,status,ctime,sid)
      cur.execute(query)
      callid=str(cur.lastrowid)
      print callid+"   "+bid+"  "+phone+"   "+status+"   "+attempts
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
        query="insert into callLogs1 (callid,retry,bid,vendor,phone,sid,callStartTime,duration,status,audio) values (%s,%s,%s,'%s','%s','%s','%s','%s','%s','%s')" % (str(callid),str(retry),bid,vendor,phone,vendorcid,ctime,duration,status,callparams)
        cur.execute(query)
if __name__ == '__main__':
  main()
