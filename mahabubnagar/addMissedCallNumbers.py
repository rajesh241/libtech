import MySQLdb
import datetime
import os
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../includes/')
import settings
import libtechFunctions
from libtechFunctions import singleRowQuery,addJobcardPhoneV1 
from settings import dbhost,dbuser,dbpasswd,sid,token
import requests
import xml.etree.ElementTree as ET


def main():
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use libtech"
  cur.execute(query)
  query="select phone from ghattuMissedCalls group by phone " 
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    phone=row[0]
    print phone
    query="use libtech"
    cur.execute(query)
    query="select jobcard from ghattuMissedCallsLog where phone='%s' and jobcard is not NULL order by id DESC limit 1" % phone
    cur.execute(query)
    if cur.rowcount == 1: 
      row=cur.fetchone()
      jobcard=row[0] 
      status=addJobcardPhoneV1(cur,phone,jobcard,'mahabubnagar')
      print phone+"  "+jobcard+"   "+status

if __name__ == '__main__':
  main()
