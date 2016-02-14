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
  jobcard='CH-05-007-026-002/141'
  phone='9246522344'
#  phone='9845155447'
  phone='9845065241'
#  phone='9833419391'
  dbname='mahabubnagar'
  dbname='surguja'
  scheduleWageBroadcastCall(cur,jobcard,phone,dbname,260846,1)
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
