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
from settings import dbhost,dbuser,dbpasswd,sid,token
from urlparse import urlparse
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapper, getForm, getButton, getButtonV2,getCenterAligned

def main():
  form = cgi.FieldStorage()
  bid=form["bid"].value
  name=form["name"].value
  formType=form["formType"].value
  if formType == 'downloadDetailReport':
    nameNoSpace=bid+"_"+name.replace(" ","")+"_detailed.csv"
  else:
    nameNoSpace=bid+"_"+name.replace(" ","")+".csv"
  fullurl = os.environ["REQUEST_URI"]
  fullurl= "http://chaupal.libtech.info" 
  o = urlparse(fullurl)
  baseURL="http://"+o.netloc
  redirectURL="http://www.google.com"
  #redirectURL="http://chaupal.libtech.info/reports/summary/%s" % nameNoSpace 
  redirectURL=baseURL+"/broadcasts/reports/broadcasts/%s" % nameNoSpace
#  redirectURL="/broadcasts/reports/broadcasts/%s" % nameNoSpace 
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
