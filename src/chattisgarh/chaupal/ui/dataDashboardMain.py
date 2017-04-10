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
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapper, getForm, getButton, getButtonV2,getCenterAligned,bsQuery2HTMLLinkV1,bsQuery2HtmlV3,getButtonV3
from libtechFunctions import writecsv

def main():
  print 'Content-type: text/html'
  print
  myhtml='' 
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  myhtml=""
  form = cgi.FieldStorage()
  districtName='none'
  blockName='none'
  panchayatName='none'
  blockCode='none'
  panchayatCode='none'
  headerText=''
  if 'district' in form:
    districtName=form['district'].value
    headerText+=districtName.upper()
  if 'block' in form:
    blockName=form['block'].value
    headerText+='-'+blockName.upper()
  if 'blockCode' in form:
    blockCode=form['blockCode'].value
  if 'panchayat' in form:
    panchayatName=form['panchayat'].value
    headerText+='-'+panchayatName.upper()
  if 'panchayatCode' in form:
    panchayatCode=form['panchayatCode'].value
  
  myhtml+=  getCenterAligned('<h2 style="color:blue"> %s</h2>' %(headerText) )
  if districtName == 'none':
    query="use libtech"
    cur.execute(query)
    query="select name districts from crawlDistricts"
    hiddenNames=['district'] 
    hiddenValues=[0]
    query_table = "<br />"
    query_table += bsQuery2HTMLLinkV1(cur, query,hiddenNames=hiddenNames,hiddenValues=hiddenValues)
    myhtml+=query_table
  elif blockName == 'none':
    query="use %s" % (districtName)
    cur.execute(query)
    query="select name blocks,DATABASE(),blockCode from blocks where isActive=1"
    hiddenNames=['district','block','blockCode'] 
    hiddenValues=[1,0,2]
    query_table = "<br />"
    query_table += bsQuery2HTMLLinkV1(cur, query,hiddenNames=hiddenNames,hiddenValues=hiddenValues)
    myhtml+=query_table
  elif panchayatName == 'none':
    query="use %s" % (districtName)
    cur.execute(query)
    query="select p.name panchayats,DATABASE(),b.name,b.blockCode,p.panchayatCode from blocks b, panchayats p where p.blockCode=b.blockCode and b.blockCode='%s' and p.isActive=1 order by p.name;" % (blockCode) 
    hiddenNames=['district','block','blockCode','panchayat','panchayatCode'] 
    hiddenValues=[1,2,3,0,4]
    query_table = "<br />"
    query_table += bsQuery2HTMLLinkV1(cur, query,hiddenNames=hiddenNames,hiddenValues=hiddenValues)
    myhtml+=query_table

  if districtName == 'none':
    query_table="<p> Select the District to Get Started</p>"
  else:
    query="use libtech"
    cur.execute(query)
    query="select id,title from reportQueries"
    myForm=getButtonV3('./viewReportHTMLV2.py','viewHTML','View HTML')
    myFormExtraInputs='<input type="hidden" name="district" value="%s"><input type="hidden" name="blockCode" value="%s"><input type="hidden" name="panchayatCode" value="%s">' % (districtName,blockCode,panchayatCode)
    myForm = myForm.replace('extrainputs','extrainputs'+myFormExtraInputs)
    hiddenNames=['formID'] 
    hiddenValues=[0]
    query_table =bsQuery2HtmlV3(cur, query,extraLabel='Edit',extra=myForm,hiddenNames=hiddenNames,hiddenValues=hiddenValues)
  myhtml+=query_table
  myhtml=htmlWrapper(title="Reports Page", head='<h1 aling="center">Reports Page</h1>', body=myhtml)
  print myhtml.encode('UTF-8')

# query="use surguja"
# cur.execute(query)
##Now we need to write the html
# query="select id,title from reportQueries"
# section_html = getButtonV2('./dataReportPost.py', 'downloadReport', 'Download')
# hiddenNames=['title'] 
# hiddenValues=[1]
# query_table = "<br />"
# query_table += bsQuery2HtmlV2(cur, query, query_caption="",extraLabel='Download',extra=section_html,hiddenNames=hiddenNames,hiddenValues=hiddenValues)
# myhtml+=query_table
# myhtml=htmlWrapper(title="Chaupal Reports", head='<h1 aling="center">Chaupal Reports</h1>', body=myhtml)
# print myhtml.encode('UTF-8')
# 

if __name__ == '__main__':
  main()
