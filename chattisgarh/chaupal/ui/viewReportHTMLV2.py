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
from libtechFunctions import writecsv,getPanchayatNameV1,getBlockNameV1

def main():
  print 'Content-type: text/html'
  print
  myhtml='' 
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  reportType='dataReport'
  form = cgi.FieldStorage()
  blockCode=form["blockCode"].value
  districtName=form["district"].value
  panchayatCode=form["panchayatCode"].value
  query="use %s" %(districtName)
  formID=form["formID"].value
  if blockCode=='none':
    blockName='ALL BLOCKS'
    blockFilterQuery=""
  else:
    blockName=getBlockNameV1(cur,districtName.lower(),blockCode)
    blockFilterQuery=" and b.blockCode="+str(blockCode)
  if panchayatCode=='none':
    panchayatName='ALL PANCHAYATS'
    panchayatFilterQuery=""
  else:
    panchayatName=getPanchayatNameV1(cur,districtName.lower(),blockCode,panchayatCode)
    panchayatFilterQuery=" and p.panchayatCode="+str(panchayatCode)
  
  query="use libtech"
  cur.execute(query)
  query="select title,dbname,selectClause,whereClause,orderClause,dbname,groupClause from reportQueries where id=" + str(formID)
  cur.execute(query)
  row=cur.fetchone()
  title=row[0]
  dbname=row[1]
  selectClause=row[2]
  whereClause=row[3]
  orderClause=row[4]
  groupClause=row[6]
  query="use "+districtName
  cur.execute(query)
  if groupClause is None:
    query=selectClause+" where "+whereClause+blockFilterQuery+panchayatFilterQuery+"  order by  "+orderClause+" limit 50"
  else: 
    query=selectClause+" where "+whereClause+blockFilterQuery+panchayatFilterQuery+" group by "+groupClause+"  order by  "+orderClause+" limit 50"
  queryWithoutLimit=query.replace("limit 50"," ")
  queryTable=bsQuery2HtmlV2(cur,query)
  queryTable=queryTable.replace('query_text',query) 
  myForm=getButtonV3('./downloadReport.py','downloadReport','Download Report')
  myFormExtraInputs='<input type="hidden" name="reportType" value="%s"><input type="hidden" name="dbname" value="%s"><input type="hidden" name="title" value="%s"><input type="hidden" name="blockName" value="%s"><input type="hidden" name="panchayatName" value="%s"><input type="hidden" name="query" value="%s">' % (reportType,districtName,title,blockName,panchayatName,queryWithoutLimit)
  myForm = myForm.replace('extrainputs',myFormExtraInputs)
  myhtml=''
  myhtml+=  getCenterAligned('<h3 style="color:green"> %s-%s</h3>' % (blockName.upper(),panchayatName.upper()))
  #myhtml+=  getCenterAligned('<h3 style="color:green"> %s</h3>' % groupClause)
  myhtml+=  getCenterAligned('<h3 style="color:green"> %s</h3>' % getString(myForm))

  myhtml+= queryTable
##Now we need to write the html
# query="select id,title from reportQueries"
# cur.execute(query)
# results = cur.fetchall()
# field_names = [i[0] for i in cur.description]
# num_fields = len(cur.description)
#
#
# queryTable='''
#    <div class="container">
#    <table class="table table-striped">
#    <thead>
#     <tr>'''
#
# for field_name in field_names:
#   queryTable += "<th>" + field_name.strip() + "</th>"
# queryTable+="</tr></thead><tbody>"
#
# for row in results:
#   i=0
#   queryTable+="<tr>"
#   while i < num_fields:
#     queryTable += "<td>" + getString(row[i]) + "</td>"
#     i += 1
#   #Lets get input form
#   formID=row[0]
#   blockCode='all'
#   panchayatCode='all'
#   myForm=getButtonV3('./viewReport.py','viewHTML','View HTML')
#   myFormExtraInputs='<input type="hidden" name="formID" value="%s"><input type="hidden" name="blockCode" value="%s"><input type="hidden" name="panchayatCode" value="%s">' % (formID,blockCode,panchayatCode)
#   myForm = myForm.replace('extrainputs',myFormExtraInputs)
#   queryTable += "<td>" + getString(myForm) + "</td>"
#   queryTable+="</tr>"
#
# queryTable+="</tbody></table></div>"
#
# myhtml+=queryTable
  myhtml=htmlWrapper(title="View Chaupal Report", head='<h1 aling="center">'+title+'</h1>', body=myhtml)
  print myhtml.encode('UTF-8')
# 

if __name__ == '__main__':
  main()
