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
  query="select bid,phone,id from callLogs where callid is NULL"
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    bid=str(row[0])
    phone=row[1]
    rowid=str(row[2])
    print rowid
#    print bid+"  "+phone
    query="select callid from callSummary where bid=%s and phone='%s'" % (bid,phone)
#    print query
    cur.execute(query)
    if(cur.rowcount == 1):
      row1=cur.fetchone()
      callid=str(row1[0])
      query="update callLogs set callid=%s where id=%s" % (callid,rowid)
    else:
      query="update callLogs set callid=0 where id=%s" % rowid
 #   print query
    cur.execute(query)
if __name__ == '__main__':
  main()
