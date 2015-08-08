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

from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapper, getForm, getButton, getButtonV2,getCenterAligned

def main():
  print 'Content-type: text/html'
  print 
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use surguja"
  cur.execute(query)
  form = cgi.FieldStorage()
  blockCode=form["blockCode"].value
  panchayatCode=form["panchayatCode"].value
  query='''
select surguja.jobcardRegister.jobcard jobcard,Group_CONCAT(surguja.jobcardDetails.applicantName ) names, libtech.jobcardPhone.phone phone,surguja.jobcardRegister.caste,surguja.jobcardRegister.village from surguja.jobcardDetails,surguja.jobcardRegister left join libtech.jobcardPhone on surguja.jobcardRegister.jobcard=libtech.jobcardPhone.jobcard where surguja.jobcardRegister.blockCode='%s' and surguja.jobcardRegister.panchayatCode='%s' and surguja.jobcardDetails.jobcard=surguja.jobcardRegister.jobcard group by surguja.jobcardRegister.jobcard; 
  '''% (blockCode,panchayatCode)

  section_html = getButtonV2('./chaupalAddPhone.py', 'editContact', 'Edit')
  hiddenNames=['jobcard'] 
  hiddenValues=[0]
  query_table = "<br />"
  query_table += bsQuery2HtmlV2(cur, query, query_caption="",extraLabel='Edit',extra=section_html,hiddenNames=hiddenNames,hiddenValues=hiddenValues)
  #myhtml = getQueryTable(cur, query)

  #myhtml += getCenterAligned('<a href="#"><h5>Top</h5></a></div>') + '<br />'
  myhtml=""
  #myhtml+= '<br />' + getCenterAligned('<h5 style="color:green">Jobcard [%s] </h5>' % blockCode)
  #myhtml+= '<br />' + getCenterAligned('<h5 style="color:blue">Block [%s] </h5>' % panchayatCode)
  myhtml+=query_table
  myhtml=htmlWrapper(title="AddressBook Update", head='<h1 aling="center">Jobcard List</h1>', body=myhtml)
  print myhtml.encode('UTF-8')

if __name__ == '__main__':
  main()
