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
sys.path.insert(0, fileDir+'/../')
import settings
from settings import dbhost,dbuser,dbpasswd,sid,token
from libtechFunctions import singleRowQuery
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapper, getForm, getButton, getButtonV2,getCenterAligned

def main():
  print 'Content-type: text/html'
  print 
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use biharPDS"
  cur.execute(query)
  myhtml=''
  query="select count(*) from pdsShops"
  totalShops=singleRowQuery(cur,query)
  totalDownload=totalShops*5
  query="select count(*) from pdsShopsDownloadStatus where isDownloaded=1"
  totalSuccessDownload=singleRowQuery(cur,query)
  totalPendingDownload=totalDownload-totalSuccessDownload 
  myhtml+=  getCenterAligned('<h3 style="color:blue">  Total Shops     - %s</h3>'  % (str(totalShops)))
  myhtml+=  getCenterAligned('<h3 style="color:blue">  Total Downloads - %s</h3>'  % (str(totalDownload)))
  myhtml+=  getCenterAligned('<h3 style="color:green"> Total Success   - %s</h3>'  % (str(totalSuccessDownload)))
  myhtml+=  getCenterAligned('<h3 style="color:red">   Total Pending   - %s</h3>'  % (str(totalPendingDownload)))
  myhtml=htmlWrapper(title="Bihar PDS Download", head='<h1 aling="center">Bihar PDS Download Status</h1>', body=myhtml)
  print myhtml.encode('UTF-8')
  #print myhtml
if __name__ == '__main__':
  main()
