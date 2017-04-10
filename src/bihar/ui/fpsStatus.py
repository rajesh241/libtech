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
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
import settings
from settings import dbhost,dbuser,dbpasswd,sid,token
from wrappers.db import dbInitialize,dbFinalize

from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapper, getForm, getButton, getButtonV2,getCenterAligned

def main():
  print 'Content-type: text/html'
  print 
 
  db = dbInitialize(db="biharPDS", charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  groupInput='fpsYear,fpsMonth'
  groupInputOrder='fpsYear DESC,fpsMonth DESC'
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  query="select %s,sum(statusRemark = 'completeRecord') Delivered,sum(statusRemark = 'deliveryDateAbsent') notDelivered, sum(statusRemark = 'noDeliveryInformation') notReleased, sum(statusRemark= 'deliveryTableMissing') badHTML,count(*) from pdsShopsDownloadStatus group by %s order by %s;" %(groupInput,groupInput,groupInputOrder)
  query_table = "<br />"
  query_table+=query
  query_table += bsQuery2HtmlV2(cur, query)
  myhtml=""
 # myhtml+=  getCenterAligned('<h2 style="color:blue"> Bihar PDS Status </h2>' )
  myhtml+=query_table
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors

  myhtml=htmlWrapper(title="Bihar PDS Status", head='<h1 aling="center">Bihar PDS Status</h1>', body=myhtml)
  print myhtml.encode('UTF-8')
  #print myhtml
if __name__ == '__main__':
  main()
