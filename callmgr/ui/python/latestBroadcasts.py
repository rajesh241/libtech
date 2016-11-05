#!/usr/bin/env python


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
sys.path.insert(0, fileDir+'/../../')
import settings
from settings import dbhost,dbuser,dbpasswd,sid,token

from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapper, getForm, getButton, getButtonV2,getCenterAligned

def main():
  print 'Content-type: text/html'
  print
  myhtml = "" 
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use libtech"
  cur.execute(query)
  query="select bid,name,DATE_FORMAT(startDate,'%d-%M-%Y') startDate,total,pending,success,fail,expired,cost,successP Percentage from broadcasts where error=0 order by bid desc limit 100"
  section_html = getButtonV2('./downloadBroadcastReport.py', 'downloadReport', 'Summary Report')
  section_html += getButtonV2('./downloadBroadcastReport.py', 'downloadDetailReport', 'Detailed Report')
  hiddenNames=['bid','name'] 
  hiddenValues=[0,1]
  query_table="</br>"
  query_table += bsQuery2HtmlV2(cur, query, query_caption="",extraLabel='Edit',extra=section_html,hiddenNames=hiddenNames,hiddenValues=hiddenValues)
  myhtml+=query_table

  myhtml=htmlWrapper(title="Broadcast Report", head='<h1 aling="center">Broadcast Report</h1>', body=myhtml)
  print myhtml.encode('UTF-8')


if __name__ == '__main__':
  main()
