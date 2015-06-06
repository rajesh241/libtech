import MySQLdb
from settings import dbhost,dbuser,dbpasswd,sid,token
import datetime
import os
import time
from settings import dbhost,dbuser,dbpasswd,sid,token
import requests
import xml.etree.ElementTree as ET
import sys

sys.path.insert(0, '../includes/')
import libtechFunctions
from libtechFunctions import gethtmlheader 
from libtechFunctions import gethtmlfooter 
from libtechFunctions import singleRowQuery 

def updateBroadcastTable(cur,bid):
  query="select count(*) from callStatus where status='success' and bid="+str(bid)
  success=singleRowQuery(cur,query)
  query="select count(*) from callStatus where status='failMaxRetry' and bid="+str(bid)
  failMaxRetry=singleRowQuery(cur,query)
  query="select count(*) from callStatus where status='expired' and bid="+str(bid)
  expired=singleRowQuery(cur,query)
  query="select count(*) from callStatus where status='pending' and bid="+str(bid)
  pending=singleRowQuery(cur,query)  
  total=success+expired+failMaxRetry+pending
  print str(success)+"  "+str(failMaxRetry)+"  "+str(expired)+"  "+str(pending)+"  "+str(total)
  isComplete=0
  if(pending == 0):
   isComplete=1
  query="update broadcasts set completed="+str(isComplete)+",success="+str(success)+",fail="+str(failMaxRetry)+",expired="+str(expired)+",pending="+str(pending)+",total="+str(total)+" where bid="+str(bid) 
  print query
  cur.execute(query)


def main():
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use libtech"
  cur.execute(query)
  print "Printing Broadcast reports"
  myhtml=gethtmlheader()
  print myhtml
  query="select bid from broadcasts where bid>1000 and completed=0 and processed=1"
  print query
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    bid=row[0]
    print "Current Bid is"+str(bid)
    updateBroadcastTable(cur,bid)

if __name__ == '__main__':
  main()
