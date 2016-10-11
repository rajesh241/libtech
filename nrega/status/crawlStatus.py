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
  form = cgi.FieldStorage()
  districtName=form["districtName"].value
  
  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
 
 
  myhtml+=  getCenterAligned('<h2 style="color:blue"> %s</h2>' % (districtName.upper()))
 
  query="select * from panchayats where isRequired=1 and jobcardCrawlDate is NULL"
  cur.execute(query)
  if cur.rowcount > 0:
    myhtml+=  getCenterAligned('<h2 style="color:red"> Jobcard Not Crawled at all for %s panchayats</h2>' % (str(cur.rowcount)))
    
  query="select * from panchayats where isRequired=1 and accountCrawlDate is NULL"
  cur.execute(query)
  if cur.rowcount > 0:
    myhtml+=  getCenterAligned('<h2 style="color:red"> Accounts Not Crawled at all for %s panchayats</h2>' % (str(cur.rowcount)))

  myhtml+=  getCenterAligned('<h3 style="color:blue"> Jobcard Crawl Status</h3>')
  query="select name,DATE_FORMAT(jobcardCrawlDate,'%d-%M-%Y') jobcardCrawlDate from panchayats where isRequired=1 order by jobcardCrawlDate  ASC limit 2;"
  query_table = "<br />"
  query_table += bsQuery2HtmlV2(cur, query, query_caption="")
  myhtml+=query_table

  myhtml+=  getCenterAligned('<h3 style="color:blue"> Account Crawl Status</h3>')
  query="select name,DATE_FORMAT(accountCrawlDate,'%d-%M-%Y') accountCrawlDate from panchayats where isRequired=1 order by accountCrawlDate  ASC limit 2;"
  query_table = "<br />"
  query_table += bsQuery2HtmlV2(cur, query, query_caption="")
  myhtml+=query_table

  myhtml+=  getCenterAligned('<h3 style="color:blue"> Muster Crawl Status</h3>')
  query="select DATE(crawlDate) crawlDate,count(*) count from musters where TIMESTAMPDIFF(DAY, crawlDate, now()) < 14   group by DATE(crawlDate);"
  query_table = "<br />"
  query_table += bsQuery2HtmlV2(cur, query, query_caption="")
  myhtml+=query_table

  myhtml+=  getCenterAligned('<h3 style="color:blue"> Muster Download Status</h3>')
  query="select isDownloaded Downloaded,wdProcessed processed, wdComplete Complete,count(*) count from musters where finyear='17' group by isDownloaded,wdProcessed,wdComplete;"
  query_table = "<br />"
  query_table += bsQuery2HtmlV2(cur, query, query_caption="")
  myhtml+=query_table
  

  myhtml=htmlWrapper(title="NREGA Status", head='<h1 aling="center">Nrega Status</h1>', body=myhtml)
  print myhtml.encode('UTF-8')


  dbFinalize(db) # Make sure you put this if there are other exit paths or errors



if __name__ == '__main__':
  main()