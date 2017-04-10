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
from settings import dbhost,dbuser,dbpasswd,sid,token,crawlDistrict
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
  query="use %s" % (crawlDistrict)
  cur.execute(query)
  myhtml=''
  query="select count(*)  from musters m,blocks b, panchayats p where b.isRequired=1 and m.blockCode=b.blockCode and m.blockCode=p.blockCode and m.panchayatCode=p.panchayatCode and p.isRequired=1 and m.finyear=16  and m.musterType='10' and (m.isDownloaded=0 or m.wdError=1 or (m.wdComplete=0 and TIMESTAMPDIFF(HOUR, m.downloadAttemptDate, now()) > 48 ) )  order by TIMESTAMPDIFF(DAY, m.downloadAttemptDate, now()) desc;"
  totalMustersPendingDownload=singleRowQuery(cur,query)
  query="select count(*)  from musters m,blocks b,panchayats p where m.wdError=0 and m.isDownloaded=1 and m.wdProcessed=0  and m.blockCode=b.blockCode and m.blockCode=p.blockCode and m.panchayatCode=p.panchayatCode and p.isRequired=1  and finyear=16;"
  totalMustersPendingProcess=singleRowQuery(cur,query)
  myhtml+=  getCenterAligned('<h3 style="color:blue">  Total Musters Pending Download     - %s</h3>'  % (str(totalMustersPendingDownload)))
  myhtml+=  getCenterAligned('<h3 style="color:blue">  Total Musters Pending Process     - %s</h3>'  % (str(totalMustersPendingProcess)))
  query="select count(*)  from musters m,blocks b, panchayats p where b.isRequired=1 and m.blockCode=b.blockCode and m.blockCode=p.blockCode and m.panchayatCode=p.panchayatCode and p.isRequired=1 and m.finyear=17  and m.musterType='10' and (m.isDownloaded=0 or m.wdError=1 or (m.wdComplete=0 and TIMESTAMPDIFF(HOUR, m.downloadAttemptDate, now()) > 48 ) )  order by TIMESTAMPDIFF(DAY, m.downloadAttemptDate, now()) desc;"
  totalMustersPendingDownload=singleRowQuery(cur,query)
  query="select count(*)  from musters m,blocks b,panchayats p where m.wdError=0 and m.isDownloaded=1 and m.wdProcessed=0  and m.blockCode=b.blockCode and m.blockCode=p.blockCode and m.panchayatCode=p.panchayatCode and p.isRequired=1  and finyear=17;"
  totalMustersPendingProcess=singleRowQuery(cur,query)
  myhtml+=  getCenterAligned('<h3 style="color:blue">  Total Musters Pending Download FY17     - %s</h3>'  % (str(totalMustersPendingDownload)))
  myhtml+=  getCenterAligned('<h3 style="color:blue">  Total Musters Pending Process  FY17   - %s</h3>'  % (str(totalMustersPendingProcess)))
  myhtml=htmlWrapper(title="NREGA Download", head='<h1 aling="center">NREGA Download Status</h1>', body=myhtml)
  print myhtml.encode('UTF-8')
  #print myhtml
if __name__ == '__main__':
  main()
