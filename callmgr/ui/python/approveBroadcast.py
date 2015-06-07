#!/usr/bin/python
import cgi
import cgitb; cgitb.enable() # Optional; for debugging only
import MySQLdb
import math
import datetime
import os
import time
import requests
import xml.etree.ElementTree as ET
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../../includes/')
import libtechFunctions
import globalSettings
import settings
from settings import dbhost,dbuser,dbpasswd,sid,token
from libtechFunctions import gethtmlheader 
from libtechFunctions import gethtmlfooter 
from libtechFunctions import singleRowQuery,arrayToHTMLLine,writecsv 
from globalSettings import broadcastsReportFile,broadcastReportFilePath
def getform(bid,formtype,inputType,buttonText):
  formhtml='<form action="./approveBroadcastPost.py" method="POST"><input name="bid" value="%s" type="hidden"><input name="formType" value="%s" type="hidden"></input><input name="phone" type="%s" size="10" ></input><button type="submit">%s</button></form>' %(bid,formtype,inputType,buttonText)
  return formhtml
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
  #print "Printing Broadcast reports"
  myhtml=gethtmlheader()
  myhtml+="<h1>Approve Broadcasts Page</h1>"
  myhtml+="<p>Please be careful in approving Broadcasts. First input your number and do seperate test with both exotel and tringo. Once you successfully receive the callback, go ahead and press the approve button."
  myhtml+="<table>"
  tableArray=['Broadcast ID', 'Broadcast Name','TestExotel','TestTringo','Approve'] 
  myhtml+=arrayToHTMLLine('th',tableArray)
 # print myhtml
  query="select bid,name from broadcasts where bid>1000 and approved=0"
  #print query
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    bid=row[0]
    name=row[1]
   # print "Current Bid is"+str(bid)
    #updateBroadcastTable(cur,bid)
    exotelhtml=getform(str(bid),'exotel','text','Test Exotel')
    tringohtml=getform(str(bid),'tringo','text','Test Tringo')
    approvehtml=getform(str(bid),'approve','hidden','Approve')
    tableArray=[bid,name,exotelhtml,tringohtml,approvehtml] 
    myhtml+=arrayToHTMLLine('td',tableArray)
    #write csv report
  myhtml+="</table>"
  myhtml+=gethtmlfooter()
  print myhtml

if __name__ == '__main__':
  main()
