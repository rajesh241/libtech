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

  form = cgi.FieldStorage()
  title=form["title"].value
  titleNoSpace=title.replace(" ","")+".csv"

  redirectURL="http://www.google.com"
  redirectURL="http://chaupal.libtech.info/data/Summary/%s" % titleNoSpace
  print 'Content-Type: text/html'
  print 'Location: %s' % redirectURL
  print # HTTP says you have to have a blank line between headers and content
  print '<html>'
  print '  <head>'
  print '    <meta http-equiv="refresh" content="0;url=%s" />' % redirectURL
  print '    <title>You are going to be redirected</title>'
  print '  </head>' 
  print '  <body>'
  print '    Redirecting... <a href="%s">Click here if you are not redirected</a>' % redirectURL
  print '  </body>'
  print '</html>'
if __name__ == '__main__':
  main()
