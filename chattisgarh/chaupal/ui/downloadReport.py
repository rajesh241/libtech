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
from bootstrap_utils import getString,bsQuery2Html, bsQuery2HtmlV2,htmlWrapper, getForm, getButtonV3, getButtonV2,getCenterAligned
from libtechFunctions import writecsv,getPanchayatName,getBlockName

def main():
  myhtml='' 
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use surguja"
  cur.execute(query)

  form = cgi.FieldStorage()
  title=form["title"].value
  query=form["query"].value
  reportType=form["reportType"].value
  title1=title.replace(" ","")
  if reportType=='misc':
    suffix=reportType+"/"+title1+".csv"
  else:
    blockName=form["blockName"].value
    panchayatName=form["panchayatName"].value
    blockName1=blockName.replace(" ","")
    panchayatName1=panchayatName.replace(" ","")
    suffix=title1+"/"+title1+"_"+blockName1+"_"+panchayatName1+".csv"
  filename=chaupalDataSummaryReportDir+"/"+suffix
  #filename=filename.lower()
  dir1 = os.path.dirname(filename)

  try:
    os.stat(dir1)
  except:
    os.mkdir(dir1)
  writecsv(cur,query,filename)
  redirectURL="http://chaupal.libtech.info/reports/summary/"+suffix
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

# linkhtml='<a href="'+downloadLink+'">Download By Clicking Here</a>'
# myhtml=''
# myhtml+=  getCenterAligned('<h3 style="color:green"> %s-%s</h3>' % (blockName.upper(),panchayatName.upper()))
# myhtml+=  getCenterAligned('<h3 style="color:green"> %s</h3>' % (linkhtml))
# 
# myhtml=htmlWrapper(title="Download Chaupal Report", head='<h1 aling="center">'+title+'</h1>', body=myhtml)
# print myhtml.encode('UTF-8')
# 

if __name__ == '__main__':
  main()
