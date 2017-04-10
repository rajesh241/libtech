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
  query="select callid,callStartTime,duration from callSummary where bid<300 and status='success' ;"
  query="select cl.id,cs.callid,cs.callStartTime,cs.phone,cs.bid,count(*) count from callSummary cs, callLogs cl where cs.callid=cl.callid and cs.callStartTime=cl.callStartTime and cs.bid=cl.bid and cs.phone=cl.phone and cs.vendor != 'awazde' and cs.duration=cl.duration and cs.status='success'  and cs.bid < 300 group by cs.callid order by count(*)"
  query="select cl.id,cs.callid,cs.callStartTime,cs.phone,cs.bid count from callSummary cs, callLogs cl where cs.callid=cl.callid and cs.callStartTime=cl.callStartTime and cs.bid=cl.bid and cs.phone=cl.phone and cs.vendor != 'awazde' and cs.duration=cl.duration and cs.status='success'  and cs.bid < 300;"
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    myid=str(row[0])
    query="update callLogs set status='pass' where id=%s " %(myid)
    print query
    cur.execute(query)


if __name__ == '__main__':
  main()
