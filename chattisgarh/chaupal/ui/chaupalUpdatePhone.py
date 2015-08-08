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
import chaupalAddPhone
from chaupalAddPhone import gotoJobcardListForm 
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapper, getForm, getButton, getButtonV2,getCenterAligned

def main():
  print 'Content-type: text/html'
  print 
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use libtech"
  cur.execute(query)
  form = cgi.FieldStorage()
  blockCode=form["blockCode"].value
  panchayatCode=form["panchayatCode"].value
  blockName=form["blockName"].value
  panchayatName=form["panchayatName"].value
  jobcard=form["jobcard"].value
  oldphone=form["oldphone"].value
  jobcardListForm=gotoJobcardListForm(blockCode,panchayatCode,'Go Back To Jobcard List')
  myhtml=""
  try:
    phone=form["phone"].value
  except:
    phone='Invalid'

  if len(phone) == 10:
    myhtml+= '<br />' + getCenterAligned('<h5 style="color:green">Jobcard [%s] </h5>' % jobcard)
    myhtml+= '<br />' + getCenterAligned('<h5 style="color:blue">Block [%s] </h5>' % blockName)
    myhtml+= '<br />' + getCenterAligned('<h5 style="color:blue">Panchayat [%s] </h5>' % panchayatName)
    myhtml+= '<br />' + getCenterAligned('<h5 style="color:blue">phone [%s] </h5>' % phone)
    myhtml+= '<br />' + getCenterAligned('<h5 style="color:blue">Old Phone  [%s] </h5>' % oldphone)
    
    query="delete from addressbook where phone='%s'" % oldphone
    myhtml+= '<br />' + getCenterAligned('<h5 style="color:red"> %s</h5>' % query )
    cur.execute(query)

    query="select id from addressbook where phone='"+phone+"'"
    cur.execute(query)
    if (cur.rowcount == 0):
      query="insert into addressbook (district,block,panchayat,phone) values ('surguja','%s','%s','%s');" %(blockName.lower(),panchayatName.lower(),phone)
    else:
      query="update addressbook set district='surguja',block='%s',panchayat='%s' where phone='%s'" %(blockName.lower(),panchayatName.lower(),phone)
    myhtml+= '<br />' + getCenterAligned('<h5 style="color:red"> %s</h5>' % query )

    cur.execute(query)

    query="select id from jobcardPhone where jobcard='"+jobcard+"'"
    #myhtml+= '<br />' + getCenterAligned('<h5 style="color:red"> %s</h5>' % query )
    cur.execute(query)
    if (cur.rowcount == 0):
      query="insert into jobcardPhone (jobcard,phone) values ('%s','%s')" % (jobcard,phone)
    else:
      query="update jobcardPhone set phone='%s' where jobcard='%s'" %(phone,jobcard)
   # myhtml+= '<br />' + getCenterAligned('<h5 style="color:red"> %s</h5>' % query )
    cur.execute(query)
    myhtml+= '<br />' + getCenterAligned('<h2 style="color:green">AddressBook Updated' )
  else:
    myhtml+= '<br />' + getCenterAligned('<h5 style="color:red"> Invalid Phone Entered</h5>' )


  myhtml+=getCenterAligned(jobcardListForm)
  myhtml=htmlWrapper(title="Update Address Book", head='<h1 align="center">Update Phone Number</h1>', body=myhtml)
  print myhtml.encode('UTF-8')

if __name__ == '__main__':
  main()
