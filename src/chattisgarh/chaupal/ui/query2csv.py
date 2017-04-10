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
from settings import dbhost,dbuser,dbpasswd
from bootstrap_utils import getString,bsQuery2Html, bsQuery2HtmlV2,htmlWrapper, getForm, getButtonV3, getButtonV2,getCenterAligned
from libtechFunctions import writecsv,getPanchayatName,getBlockName

def main():
  print 'Content-type: text/html'
  print
  myhtml='' 
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  myForm=getButtonV3('./downloadReport.py','downloadReport','Download Report')
  myFormExtraInputs='Title:<input type="text" name="title" ></br>DatabaseName:<input type="text" name="dbname" ></br><input type="hidden" name="reportType" value="misc">Query<input type="text" name="query" ></br>' 
  myForm = myForm.replace('extrainputs',myFormExtraInputs)
  myhtml=''
  myhtml+=  getCenterAligned('<h3 style="color:green"> %s</h3>' % getString(myForm))

  myhtml=htmlWrapper(title="Query to CSV", head='<h1 aling="center">Query to CSV Utility</h1>', body=myhtml)
  print myhtml.encode('UTF-8')
# 

if __name__ == '__main__':
  main()
