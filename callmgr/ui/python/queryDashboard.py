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
import processBroadcasts
from processBroadcasts import getGroupQueryMatchString,getLocationQueryMatchString 
from settings import dbhost,dbuser,dbpasswd,sid,token
from libtechFunctions import gethtmlheader 
from libtechFunctions import gethtmlfooter 
from libtechFunctions import singleRowQuery,arrayToHTMLLine,writecsv 
from globalSettings import broadcastsReportFile,broadcastReportFilePath

from bootstrap_utils import bsQuery2Html,htmlWrapper, getForm, getCenterAligned

def getQueryTable(cur):
  query = 'select * from queryDB'
  field_names = ['Query No', 'Query', 'Go To']
  section_html = '<a href="#querysection_tag">section_text</a>'
  
  query_table = "<br />"
  query_table += bsQuery2Html(cur, query, query_caption="", field_names=field_names, extra=section_html)
  query_table += getForm(0, './queryDashboardPost.py', 'queryMake', 'Go')
  return query_table

def queryDB():
  print 'Content-type: text/html'
  print 
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use libtech"
  cur.execute(query)
  query='select qid,query from queryDB'
  cur.execute(query)
  queries = cur.fetchall()

  myhtml = getQueryTable(cur)
  
  for row in queries:
    qid = row[0]
    query = row[1]
    query_caption = '<div id=query%d>Query: #%d <a name=query%d></a></div>' % (qid, qid, qid)
#    query_caption = 'Query <a href="#%d">#%d</a>' % (qid, qid)
    myhtml += bsQuery2Html(cur,query, query_caption)
    myhtml += getCenterAligned('<a href="#"><h5>Top</h5></a></div>') + '<br />'
  
  myhtml=htmlWrapper(title="Query Dashboard", head='<h1 aling="center"><a href="./queryDashboard.py">Query Dashboard</a></h1>', body=myhtml)
  return myhtml


def main():
  print queryDB()

if __name__ == '__main__':
  main()
