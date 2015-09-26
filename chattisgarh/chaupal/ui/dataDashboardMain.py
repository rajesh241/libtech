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
import libtechFunctions
import globalSettings
import settings
from globalSettings import chaupalDataSummaryReportDir,chaupalDashboardLink,chaupalDataDashboardLink,chaupalDataDashboardLimit
from settings import dbhost,dbuser,dbpasswd,sid,token
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapper, getForm, getButton, getButtonV2,getCenterAligned
from libtechFunctions import writecsv

def main():
  print 'Content-type: text/html'
  print
  myhtml='' 
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use surguja"
  cur.execute(query)
##Now we need to write the html
  query="select id,title from reportQueries"
  section_html = getButtonV2('./dataReportPost.py', 'downloadReport', 'Download')
  hiddenNames=['title'] 
  hiddenValues=[1]
  query_table = "<br />"
  query_table += bsQuery2HtmlV2(cur, query, query_caption="",extraLabel='Download',extra=section_html,hiddenNames=hiddenNames,hiddenValues=hiddenValues)
  myhtml+=query_table
  myhtml=htmlWrapper(title="Chaupal Reports", head='<h1 aling="center">Chaupal Reports</h1>', body=myhtml)
  print myhtml.encode('UTF-8')
# 

if __name__ == '__main__':
  main()
