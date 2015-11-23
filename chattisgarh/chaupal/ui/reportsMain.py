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
from libtechFunctions import writecsv
def getLocationSelectCode(cur,locationType):
  if locationType=='block':
    myhtml='Block:<select name="blockCode" >'
    query="select name,blockCode from blocks where isActive=1"
  elif locationType=='panchayat':
    query="select name,panchayatCode from panchayats where isSurvey=1"
    myhtml='Panchayat:<select name="panchayatCode" >'
  myhtml+='<option value="%s">%s </option>' %('all','ALL')
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    blockName=row[0]
    blockCode=row[1]
    myhtml+='<option value="%s">%s </option>' %(blockCode,blockName)
  myhtml+='</select>'
  return myhtml
     
def main():
  print 'Content-type: text/html'
  print
  myhtml='' 
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use surguja"
  cur.execute(query)

  myhtml=''
##Now we need to write the html
  query="select id,title from reportQueries"
  cur.execute(query)
  results = cur.fetchall()
  field_names = [i[0] for i in cur.description]
  num_fields = len(cur.description)


  queryTable='''
     <div class="container">
     <table class="table table-striped">
     <thead>
      <tr>'''

  for field_name in field_names:
    queryTable += "<th>" + field_name.strip() + "</th>"
  queryTable+="</tr></thead><tbody>"

  for row in results:
    i=0
    queryTable+="<tr>"
    while i < num_fields:
      queryTable += "<td>" + getString(row[i]) + "</td>"
      i += 1
    #Lets get input form
    formID=row[0]
    blockCode='005'
    panchayatCode='032'
    myForm=getButtonV3('./viewReportHTML.py','viewHTML','View HTML')
    blockSelect=getLocationSelectCode(cur,'block')
    panchayatSelect=getLocationSelectCode(cur,'panchayat')
    myFormExtraInputs='<input type="hidden" name="formID" value="%s"><input type="hidden" name="blockCode1" value="%s"><input type="hidden" name="panchayatCode1" value="%s">%s%s' % (formID,blockCode,panchayatCode,blockSelect,panchayatSelect)
    myForm = myForm.replace('extrainputs',myFormExtraInputs)
    queryTable += "<td>" + getString(myForm) + "</td>"
    queryTable+="</tr>"

  queryTable+="</tbody></table></div>"

  myhtml+=queryTable
  myhtml=htmlWrapper(title="Chaupal Reports", head='<h1 aling="center">Chaupal Reports</h1>', body=myhtml)
  print myhtml.encode('UTF-8')
# 

if __name__ == '__main__':
  main()
