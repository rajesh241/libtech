#!/usr/bin/python
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
from broadcastFunctions import gettringoaudio,getaudio,scheduleGeneralBroadcastCall 

def main():
  print 'Content-type: text/html'
  print 
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use libtech"
  cur.execute(query)
  myhtml=gethtmlheader()
  form = cgi.FieldStorage()
  bid=form["bid"].value
  phone=form["phone"].value
 
  vendor='exotel'
  #vendor=formType
  scheduleGeneralBroadcastCall(cur,bid,phone,vendor,1)



if __name__ == '__main__':
  main()
