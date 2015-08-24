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
  query="select name from blocks where blockCode='%s'" % blockCode
  cur.execute(query)
  row=cur.fetchone()
  blockName=row[0]
  query="select name from panchayats where blockCode='%s' and panchayatCode='%s'" % (blockCode,panchayatCode)
  cur.execute(query)
  row=cur.fetchone()
  panchayatName=row[0]


  query='''
select surguja.jobcardRegister.jobcard jobcard,Group_CONCAT(surguja.jobcardDetails.applicantName ) names, libtech.jobcardPhone.phone phone,surguja.jobcardRegister.caste,surguja.jobcardRegister.village from surguja.jobcardDetails,surguja.jobcardRegister left join libtech.jobcardPhone on surguja.jobcardRegister.jobcard=libtech.jobcardPhone.jobcard where surguja.jobcardRegister.blockCode='%s' and surguja.jobcardRegister.panchayatCode='%s' and surguja.jobcardDetails.jobcard=surguja.jobcardRegister.jobcard  group by surguja.jobcardRegister.jobcard order by surguja.jobcardRegister.jcNumber; 
  '''% (blockCode,panchayatCode)

  section_html = getButtonV2('./chaupalAddPhone.py', 'editContact', 'Edit')
  addNumberForm = getButtonV2('./chaupalAddPhone.py', 'addNumbers', 'Add Numbers without Jobcards')
  addNumberFormExtraInputs='<input type="hidden" name="blockCode" value="%s"><input type="hidden" name="panchayatCode" value="%s">' % (blockCode,panchayatCode)
  addNumberForm = addNumberForm.replace('extrainputs',addNumberFormExtraInputs)
  hiddenNames=['jobcard'] 
  hiddenValues=[0]
  query_table = "<br />"
  query_table += bsQuery2HtmlV2(cur, query, query_caption="",extraLabel='Edit',extra=section_html,hiddenNames=hiddenNames,hiddenValues=hiddenValues)
  #myhtml = getQueryTable(cur, query)

  #myhtml += getCenterAligned('<a href="#"><h5>Top</h5></a></div>') + '<br />'
  query="use libtech"
  cur.execute(query)
  query="select count(*) from addressbook where district='surguja' and block='%s' and panchayat='%s'" % (blockName.lower(),panchayatName.lower())
  cur.execute(query)
  row=cur.fetchone()
  totalNumbers=row[0]
  goBackPanchayat = getButtonV2('./panchayatList.py', 'panchayatList', 'Panchayat List')
  goBackPanchayat = goBackPanchayat.replace('extrainputs',addNumberFormExtraInputs)

  myhtml=""
  myhtml+=  getCenterAligned('<h2 style="color:blue"> %s-%s</h2>' % (blockName.upper(),panchayatName.upper()))
  myhtml+=  getCenterAligned('<h2 style="color:blue"> %s</h2>' % goBackPanchayat) 
  myhtml+=  getCenterAligned('<h5 style="color:purple"> Total Numbers - %s</h5>' % (str(totalNumbers)))
  myhtml+=  getCenterAligned(addNumberForm)
  myhtml+=  getCenterAligned('<h3 style="color:green"> Jobcard List</h3>' )
  #myhtml+= '<br />' + getCenterAligned('<h5 style="color:green">Jobcard [%s] </h5>' % blockCode)
  #myhtml+= '<br />' + getCenterAligned('<h5 style="color:blue">Block [%s] </h5>' % panchayatCode)
  myhtml+=query_table
  myhtml+=  getCenterAligned('<h3 style="color:red">Phone Numbers with Multiple jobcards</h3>' )
  query="select phone,count(*) count, GROUP_CONCAT(jobcard SEPARATOR ',') jobcards from jobcardPhone where jobcard like '%CH-05-"+blockCode+"-"+panchayatCode+"%' group by phone having count(*) > 1;" 
  query_table = "<br />"
  query_table += bsQuery2HtmlV2(cur, query, query_caption="")
  myhtml+=query_table


  myhtml+=  getCenterAligned('<h3 style="color:green"> Phone Numbers Without Jobcards</h3>' )
  query="select phone,block,panchayat from addressbook where phone not in (select phone from jobcardPhone) and district='surguja' and block='%s' and panchayat='%s'" % (blockName.lower(),panchayatName.lower())
  deleteNumberForm = getButtonV2('./chaupalUpdatePhone.py', 'deleteNumber', 'Delete Number')
  deleteNumberForm = deleteNumberForm.replace('extrainputs','extrainputs'+addNumberFormExtraInputs)
  hiddenNames=['phone'] 
  hiddenValues=[0]
  query_table = "<br />"
  query_table += bsQuery2HtmlV2(cur, query, query_caption="",extraLabel='Edit',extra=deleteNumberForm,hiddenNames=hiddenNames,hiddenValues=hiddenValues)
  # 
  myhtml+=query_table

  myhtml=htmlWrapper(title="AddressBook Update", head='<h1 aling="center">Address Book</h1>', body=myhtml)
  print myhtml.encode('UTF-8')

if __name__ == '__main__':
  main()
