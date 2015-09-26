#!/usr/bin/env python

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
import libtechFunctions
import globalSettings
import settings
from globalSettings import chaupalDataSummaryReportDir,chaupalDashboardLink,chaupalDataDashboardLink,chaupalDataDashboardLimit
from settings import dbhost,dbuser,dbpasswd,sid,token
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapper, getForm, getButton, getButtonV2,getCenterAligned
from libtechFunctions import writecsv

def main():
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use surguja"
  cur.execute(query)
  queryType='data'
  query="select id,title,query,locationFilter,finyearFilter,dbname from reportQueries where type='%s' order by id desc" % queryType
  cur.execute(query)
  queries=cur.fetchall()
  for row in queries:
    dbname=row[5]
    query="use %s" % dbname
    cur.execute(query)
    title=row[1]
    query=row[2]
    finyearFilter=row[4]
    if finyearFilter is not None:
      finyearFilter=row[4].replace("myFinYear","16")
      query=query.replace("additionalFilters"," and "+finyearFilter)
    titleNoSpace=title.replace(" ","")
    csvfilename=chaupalDataSummaryReportDir+titleNoSpace+".csv"
 
    print query
    print csvfilename
    writecsv(cur,query,csvfilename)

if __name__ == '__main__':
  main()
