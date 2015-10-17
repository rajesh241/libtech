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
sys.path.insert(0, fileDir+'/../includes/')
import libtechFunctions
import broadcastFunctions
import globalSettings
import settings
from settings import dbhost,dbuser,dbpasswd,sid,token
from libtechFunctions import getjcNumber,singleRowQuery,getBlockCodeFromJobcard,getPanchayatCodeFromJobcard,getBlockName,getPanchayatName,addPhoneAddressBook

from broadcastFunctions import getWageBroadcastAudioArray,scheduleWageBroadcastCall
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
  query="select mt.id,mt.jobcard,mt.musterNo,mt.finyear,mt.accountNo,mt.totalWage,mt.creditedDate,mt.bankNameOrPOName,mt.blockCode,mt.panchayatCode from musterTransactionDetails mt,panchayats p where mt.blockCode=p.blockCode and mt.panchayatCode=p.panchayatCode and mt.status='Credited' and mt.creditedDate > '2015-07-30' and mt.bankNameOrPOName LIKE '%BANK%' order by mt.creditedDate"
#  query="select mt.id,mt.jobcard,mt.musterNo,mt.finyear,mt.accountNo,mt.totalWage,mt.creditedDate from musterTransactionDetails mt,panchayats p where mt.blockCode=p.blockCode and mt.panchayatCode=p.panchayatCode and mt.status='Credited' and mt.creditedDate > '2015-07-30' order by mt.creditedDate DESC "
  cur.execute(query)
  results = cur.fetchall()
  query="use libtech"
  cur.execute(query)
  for row in results:
    musterTransactionID=str(row[0])
    jobcard=row[1]
    musterNo=str(row[2])
    finyear=row[3]
    accountNo=str(row[4])
    totalWage=str(row[5])
    creditedDate=row[6]
    blockCode=row[8]
    panchayatCode=row[9]
    query="select * from wageBroadcast where jobcard='%s' and musterNo='%s' and accountNo='%s' and finyear='%s' and source='cron'" %(jobcard,musterNo,accountNo,finyear)
    cur.execute(query)
    if cur.rowcount == 0:
      query="select phone from addressbook where phone='9845065241'"
      query="select phone from jobcardPhone where jobcard='%s'" % jobcard
      cur.execute(query)
      if cur.rowcount == 1:
        row1=cur.fetchone()
        phone=row1[0]
        query="select dnd from addressbook where phone='%s'" % phone
        dnd=singleRowQuery(cur,query)
        print jobcard+","+phone+","+dnd
        query="select * from wageBroadcast where phone='%s' and DATE(NOW()) = DATE(callScheduleDate);" %(phone)
       # phone='9483782687'
        cur.execute(query)
        if cur.rowcount == 0:
          #callid=1
          callid=scheduleWageBroadcastCall(cur,jobcard,phone,musterTransactionID,1)
          query="insert into wageBroadcast (jobcard,musterNo, accountNo,finyear,phone,wage,dnd,callid,source,callScheduleDate,creditedDate,blockCode,panchayatCode) values ('%s','%s','%s','%s','%s',%s,'%s','%s','cron',NOW(),'%s','%s','%s');" % (jobcard,musterNo,accountNo,finyear,phone,totalWage,dnd,str(callid),creditedDate,blockCode,panchayatCode)
          print query
          cur.execute(query)
#  jobcard='CH-05-005-032-001/85'
#	  phone='9845065241'
#  phone='9833419391'
#  phone='9845155447'
#  scheduleWageBroadcastCall(cur,jobcard,phone)
#  getWageBroadcastAudioArray(cur,jobcard)
# query="use surguja"
# cur.execute(query)
# query="select jobcard,id from  musterTransactionDetails"
# query="select jobcard,id from  musterTransactionDetails "
# cur.execute(query)
# results = cur.fetchall()
  
# for row in results:
#   jobcard=row[0]    
#   rowid=str(row[1])
#   print rowid+"  " +jobcard
#   blockCode=getBlockCodeFromJobcard(jobcard) 
#   panchayatCode=getPanchayatCodeFromJobcard(jobcard) 
#   query="update musterTransactionDetails set blockCode='%s',panchayatCode='%s' where id=%s" %(blockCode,panchayatCode,rowid)
#    print query
#   cur.execute(query)
#   bid=str(row[0])
#   phone=row[1]
#   tableid=str(row[2])
#   query="select sid from callLogs where bid=%s and phone='%s' and status='pass'" % (bid,phone)
#   print query
#   sid=singleRowQuery(cur,query)
#   print tableid+"  "+bid+"   "+phone+"  "+sid
#   query="update callStatus set sid='%s' where id=%s" %(sid,tableid)
#   cur.execute(query)
#   groupid=str(row[0])
#   groupName=row[1]
#   print groupid+"  "+groupName+"  "
#   queryMatchString="  groups like '%~"+groupName+"~%' "
#   query="select phone from addressbook where %s" % queryMatchString
#   cur.execute(query)
#   results1 = cur.fetchall()
#   for row1 in results1:
#     phone=row1[0]
#     print groupid+"  "+phone
#     query="insert into groupPhone (groupid,phone) values (%s,'%s');" %(groupid,phone)
#     cur.execute(query)
#    addPhoneAddressBook(cur,phone,'surguja',blockName,panchayatName) 
# query="select jobcard from jobcardRegister " 
# cur.execute(query)
# results = cur.fetchall()
# for row in results:
#   jobcard=row[0]
#   jcNumber=getjcNumber(jobcard)
#   print jcNumber+"  "+jobcard
#   query="update jobcardRegister set jcNumber=%s where jobcard='%s'" % (jcNumber,jobcard)
#  # print query
#   cur.execute(query)

if __name__ == '__main__':
  main()
