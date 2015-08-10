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
from libtechFunctions import singleRowQuery,addJobcardPhone,addPhoneAddressBook,deletePhoneAddressBook
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
  myhtml=""
  form = cgi.FieldStorage()
  blockCode=form["blockCode"].value
  panchayatCode=form["panchayatCode"].value
  formType=form["formType"].value
  if(formType == 'updateNumber'):
    blockCode=form["blockCode"].value
    panchayatCode=form["panchayatCode"].value
    blockName=form["blockName"].value
    panchayatName=form["panchayatName"].value
    jobcard=form["jobcard"].value
    oldphone=form["oldphone"].value
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
   
   
      if(jobcard== "NoJobCard"):
        status=addPhoneAddressBook(cur,phone,'surguja',blockName,panchayatName)
      else:
        status=addJobcardPhone(cur,phone,jobcard)
   
      myhtml+= '<br />' + getCenterAligned('<h2 style="color:green">AddressBook Update %s' % status)
   
   
    else:
      myhtml+= '<br />' + getCenterAligned('<h5 style="color:red"> Invalid Phone Entered</h5>' )

  elif(formType == 'deleteNumber'):
    phone=form["phone"].value
    status=deletePhoneAddressBook(cur,phone)
    myhtml+= '<br />' + getCenterAligned('<h5 style="color:red"> Phone Number Delete Successfully</h5>' )

  jobcardListForm=gotoJobcardListForm(blockCode,panchayatCode,'Go Back To Jobcard List')
  myhtml+=getCenterAligned(jobcardListForm)
  myhtml=htmlWrapper(title="Update Address Book", head='<h1 align="center">Update Phone Number</h1>', body=myhtml)
  print myhtml.encode('UTF-8')

if __name__ == '__main__':
  main()
