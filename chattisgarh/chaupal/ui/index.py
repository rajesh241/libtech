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
from settings import dbhost,dbuser,dbpasswd,sid,token
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapper, getForm, getButton, getButtonV2,getCenterAligned

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
  query="select blockCode BlockCode,name Block from blocks where isActive=1" 
  #myhtml = getQueryTable(cur, query)
  section_html = getButtonV2('./panchayatList.py', 'AddPhoneNumbers', 'Add Phone Numbers')
  hiddenNames=['blockCode'] 
  hiddenValues=[0]
  query_table = "<br />"
  query_table += bsQuery2HtmlV2(cur, query, query_caption="",extraLabel='Add Phones',extra=section_html,hiddenNames=hiddenNames,hiddenValues=hiddenValues)
  myhtml+=query_table 
  myhtml += getCenterAligned('<a href="#"><h5>Top</h5></a></div>') + '<br />'
  
  myhtml=htmlWrapper(title="Chaupal Dashboard", head='<h1 aling="center">Chaupal Dashboard</h1>', body=myhtml)
  print myhtml.encode('UTF-8')

if __name__ == '__main__':
  main()
