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



def main():
  print 'Content-type: text/html'
  print 
  myhtml=''
  myhtml+="<h2> Place Test Call </h2>"
  formhtml='<br /><form action="./testCallPost.py" method="POST">BID<input name="bid" type="text"></br>Phone<input name="phone" type="test"></br></input><button type="submit">Submit</button></form>' 
  myhtml+=formhtml
  print myhtml

if __name__ == '__main__':
  main()
