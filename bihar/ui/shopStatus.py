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
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
import settings
from settings import dbhost,dbuser,dbpasswd,sid,token
from wrappers.db import dbInitialize,dbFinalize

from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapper, getForm, getButton, getButtonV2,getCenterAligned
def getInputRow(cur,inputType,inputValue,inputDistValue=None,inputBlockValue=None):
  if inputType == 'distCode':
    query="select distCode,distName from pdsShops group by distCode"
    inputHTML='District <select name="%s" >' % (inputType)
    optionText='<option value="%s">%s </option>' % ('000','Select District')
  elif inputType == 'blockCode':
    query="select blockCode,blockName from pdsShops where distCode='%s' group by blockCode" % (inputDistValue)
    inputHTML='Block <select name="%s" >' % (inputType)
    optionText='<option value="%s">%s </option>' % ('000','Select Block')
  elif inputType == 'fpsCode':
    query="select fpsCode,fpsName from pdsShops where distCode='%s' and blockCode='%s' group by fpsCode order by fpsName" % (inputDistValue,inputBlockValue)
    inputHTML='fpsShop <select name="%s" >' % (inputType)
    optionText='<option value="%s">%s </option>' % ('000','Select FPS Shop')
  cur.execute(query)
  results=cur.fetchall()
  
  for row in results:
    inputCode=row[0]
    inputName=row[1]
    if inputCode == inputValue:
      optionText+='<option value="%s" selected>%s </option>' % (inputCode,inputName)
    else:
      optionText+='<option value="%s">%s </option>' % (inputCode,inputName)
  
  inputHTML+=optionText
  inputHTML+='</select>'
  return inputHTML
 
def main():
  print 'Content-type: text/html'
  print 
 
  db = dbInitialize(db="biharPDS", charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  
  queryFilter=' and ' 
  distCodeValue='000'
  blockCodeValue='000'
  fpsCodeValue='000' 
  noInputPassed=1
  form = cgi.FieldStorage()
  if form.has_key('distCode'):
    noInputPassed=0
    distCodeValue=form["distCode"].value
    queryFilter+="p.distCode = '%s' and " %(distCodeValue)
    if form.has_key('blockCode'):
      blockCodeValue=form["blockCode"].value
      if blockCodeValue != '000':
        noInputPassed=0
        queryFilter+="p.blockCode = '%s' and " %(blockCodeValue)
      if form.has_key('fpsCode'):
        fpsCodeValue=form["fpsCode"].value
        if fpsCodeValue != '000':
          noInputPassed=0
          queryFilter+="p.fpsCode = '%s' and " %(fpsCodeValue)
  
  if noInputPassed == 1: 
    queryFilter=queryFilter.lstrip(' and')
  queryFilter=queryFilter.rstrip('and ') 
   
  myhtml=""
  myform=getButtonV2("./shopStatus.py", "biharPDS", "Submit") 
  extraInputs=''
  extraInputs+=getInputRow(cur,"distCode",distCodeValue)
  extraInputs+=getInputRow(cur,"blockCode",blockCodeValue,distCodeValue)
  extraInputs+=getInputRow(cur,"fpsCode",fpsCodeValue,distCodeValue,blockCodeValue)
  myform=myform.replace("extrainputs",extraInputs)

  
  query_table=''
  query_table+="<center><h2>Download Status </h2></center>"
  query="select p.distName,p.blockName,p.fpsName,ps.fpsMonth,ps.fpsYear,ps.downloadAttemptDate,ps.statusRemark from pdsShops p, pdsShopsDownloadStatus ps where p.distCode=ps.distCode and p.blockCode=ps.blockCode and p.fpsCode=ps.fpsCode %s limit 30" %(queryFilter)
  query_table += bsQuery2HtmlV2(cur, query)
 
  query_table+="<center><h2>Detailed Information</h2></center>"
  query="select p.distName,p.blockName,p.fpsName,psms.fpsMonth,psms.fpsYear,psms.scheme,psms.status,psms.sioStatus,psms.driverName0,psms.vehicle0,psms.dateOfDelivery0 from pdsShops p, pdsShopsMonthlyStatus psms where p.distCode=psms.distCode and p.blockCode=psms.blockCode and p.fpsCode=psms.fpsCode %s order by dateOfDelivery0 DESC limit 100" %(queryFilter)
  query_table += bsQuery2HtmlV2(cur, query)
 
  myhtml+=myform
  #myhtml+=query
  myhtml+=query_table
 

  myhtml=htmlWrapper(title="Shop Status", head='<h1 aling="center">Bihar PDS Shop Status</h1>', body=myhtml)
  print myhtml.encode('UTF-8')
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  #print myhtml
if __name__ == '__main__':
  main()
