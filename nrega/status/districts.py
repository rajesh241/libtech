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
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
import settings
from wrappers.db import dbInitialize,dbFinalize

from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapper, getForm, getButton, getButtonV2,getCenterAligned

def main():
  print 'Content-type: text/html'
  print 
  myhtml=''  
  
  db = dbInitialize(db="crawlDistricts", charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  
  section_html = getButtonV2('./crawlStatus.py', 'status', 'status')
  query="select name from districts"
  hiddenNames=['districtName'] 
  hiddenValues=[0]
  query_table = "<br />"
  query_table += bsQuery2HtmlV2(cur, query, query_caption="",extraLabel='status',extra=section_html,hiddenNames=hiddenNames,hiddenValues=hiddenValues)
  myhtml+=query_table
  

  myhtml=htmlWrapper(title="NREGA Status", head='<h1 aling="center">Nrega Status</h1>', body=myhtml)
  print myhtml.encode('UTF-8')

  dbFinalize(db) # Make sure you put this if there are other exit paths or errors

  #print myhtml
if __name__ == '__main__':
  main()
