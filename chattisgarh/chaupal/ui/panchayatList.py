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
from settings import dbhost,dbuser,dbpasswd,sid,token
from libtechFunctions import gethtmlheader 
from libtechFunctions import gethtmlfooter 
from libtechFunctions import singleRowQuery,arrayToHTMLLine,writecsv 
from globalSettings import broadcastsReportFile,broadcastReportFilePath

from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapper, getForm, getButton, getButtonV2,getCenterAligned

def getQueryTable(cur, query):
  field_names = ['Name', 'Total Jobcards', 'Total Workers', 'Total moblies']
  #section_html = '<a href="#querysection_tag">section_text</a>'
  section_html = getButtonV2('./jobcardList.py', 'AddPhoneNumbers', 'Add Phone Numbers')
  hiddenNames=['blockCode','panchayatCode'] 
  hiddenValues=[0,1]
  query_table = "<br />"
  query_table += bsQuery2HtmlV2(cur, query, query_caption="",extraLabel='Add Phones',extra=section_html,hiddenNames=hiddenNames,hiddenValues=hiddenValues)
  return query_table

def main():
  print 'Content-type: text/html'
  print 
  form = cgi.FieldStorage()
  blockCode=form["blockCode"].value
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use surguja"
  cur.execute(query)
  query="select name from blocks where blockCode='%s'" % blockCode
  blockName=singleRowQuery(cur,query)
  myhtml=''
  #blockCode='003'
  query="select blockCode BlockCode,panchayatCode PanchayatCode,name Panchayats,totalJobcards TotalJobcards,totalWorkers TotalWorkers,totalMobiles TotalMobiles from panchayats where isSurvey=1 and blockCode="+blockCode
  myhtml+=  getCenterAligned('<h2 style="color:blue"> %s</h2>' % (blockName.upper()))
  myhtml+= getQueryTable(cur, query)

  myhtml += getCenterAligned('<a href="#"><h5>Top</h5></a></div>') + '<br />'
  
  myhtml=htmlWrapper(title="Panchayat List", head='<h1 aling="center">Panchayat List</h1>', body=myhtml)
  print myhtml.encode('UTF-8')

if __name__ == '__main__':
  main()
