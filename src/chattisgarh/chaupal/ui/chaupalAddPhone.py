#!/usr/bin/python
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
sys.path.insert(0, fileDir+'./')
import libtechFunctions
import globalSettings
import settings
from settings import dbhost,dbuser,dbpasswd,sid,token
from libtechFunctions import singleRowQuery
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapper, getForm, getButton, getButtonV2,getCenterAligned

def gotoJobcardListForm(blockCode,panchayatCode,buttonText):
  form_html = '''
  <br />
  <br />
  <form action="./jobcardList.py" method="POST">
    form_text
  </form>
'''

  form_text = '''
    <div class="row">

      <div class="col-xs-2">
      </div>

      <div class="col-xs-8">
        <div class="input-group">
          <input name="blockCode" value="blockCode_value" type="hidden">
          <input name="panchayatCode" value="panchayatCode_value" type="hidden">
          <span class="input-group-btn">
            <button type="submit" class="btn btn-default">button_text</button>
          </span>
        </div>
      </div>

      <div class="col-xs-2">
      </div>

    </div>
'''
  form_text = form_text.replace('blockCode_value', blockCode)
  form_text = form_text.replace('panchayatCode_value', panchayatCode)
  form_text = form_text.replace('button_text', buttonText)
  return form_html.replace('form_text', form_text)



def getPhoneUpdateForm(blockCode,panchayatCode,blockName,panchayatName,jobcard,phone):
    
  form_html = '''
  <form action="./chaupalUpdatePhone.py" method="POST">
    form_text
  </form>
'''

  form_text = '''
    <div class="row">

      <div class="col-xs-2">
      </div>

      <div class="col-xs-8">
        <div class="input-group">
          <input name="blockCode" value="blockCode_value" type="hidden">
          <input name="formType" value="updateNumber" type="hidden">
          <input name="panchayatCode" value="panchayatCode_value" type="hidden">
          <input name="blockName" value="blockName_value" type="hidden">
          <input name="panchayatName" value="panchayatName_value" type="hidden">
          <input name="oldphone" value="phone_value" type="hidden">
          <input name="jobcard" value="jobcard_value" type="hidden">
          <input name="phone" type="text" class="form-control" placeholder="phone_value" >
          <span class="input-group-btn">
            <button type="submit" class="btn btn-default">button_text</button>
          </span>
        </div>
      </div>

      <div class="col-xs-2">
      </div>

    </div>
'''
  form_text = form_text.replace('blockCode_value', blockCode)
  form_text = form_text.replace('panchayatCode_value', panchayatCode)
  form_text = form_text.replace('blockName_value', blockName)
  form_text = form_text.replace('panchayatName_value', panchayatName)
  form_text = form_text.replace('jobcard_value', jobcard)
  form_text = form_text.replace('phone_value', phone)
  form_text = form_text.replace('button_text', 'submit')
#  form_text = form_text.replace('query_text', query_text)

  #formhtml='<br /><form action="./queryDashboardPost.py" method="POST"><input name="qid" value="%s" type="hidden"><input name="formType" value="%s" type="hidden"></input>%s<button type="submit">%s</button></form>' %(qid, form_type, input_element, "Go")
  
#  return formhtml
  return form_html.replace('form_text', form_text)


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
  formType=form["formType"].value
  myhtml=""
  if(formType == 'editContact'):
    jobcard=form["jobcard"].value
    blockCode=jobcard[6:9]
    panchayatCode=jobcard[10:13]
    query="select b.name,p.name,jr.jobcard,jr.caste,jr.village  from jobcardRegister jr,panchayats p, blocks b where jr.blockCode=b.blockCode and jr.blockCode=p.blockCode and jr.panchayatCode=p.panchayatCode and jr.jobcard='"+jobcard+"';"
    cur.execute(query)
    row=cur.fetchone()
    blockName=row[0]
    panchayatName=row[1]
    caste=row[3]
    village=row[4]
    query="select libtech.jobcardPhone.phone from libtech.jobcardPhone where libtech.jobcardPhone.jobcard='"+jobcard+"';"
    cur.execute(query)
    phone=' '
    if(cur.rowcount == 1):
      row=cur.fetchone()
      phone=row[0]
#Now we need to get the names and account numbers
    query="select applicantName,age,gender,accountNo,primaryAccountHolder,bankNameOrPOName from jobcardDetails where jobcard='"+jobcard+"';"
    field_names = ['applicant Name', 'Age', 'Gender', 'AccountNo','primaryAccountHoler', 'Bank PostOffice']
    query_table = "<br />"
    query_table += bsQuery2Html(cur, query, query_caption="", field_names=field_names)

    myhtml+=  getCenterAligned('<h5 style="color:green">Jobcard [%s] </h5>' % jobcard)
    myhtml+=  getCenterAligned('<h5 style="color:blue">Village [%s] </h5>' % village)
    myhtml+=  getCenterAligned('<h5 style="color:red">phone [%s] </h5>' % phone)
    deleteNumberForm = getButtonV2('./chaupalUpdatePhone.py', 'deleteNumber', 'Delete this Number')
    extraInputs='<input type="hidden" name="phone" value="%s" >' % phone
    extraInputs+='<input type="hidden" name="blockCode" value="%s"><input type="hidden" name="panchayatCode" value="%s">' % (blockCode,panchayatCode)
    deleteNumberForm=deleteNumberForm.replace('extrainputs',extraInputs)
    myhtml+=getCenterAligned(deleteNumberForm)
    myhtml+=query_table
  
  elif(formType == 'addNumbers'):
    jobcard='NoJobCard'
    blockCode=form["blockCode"].value
    panchayatCode=form["panchayatCode"].value
    query="select name from blocks where blockCode='%s'" % blockCode
    blockName=singleRowQuery(cur,query)
    query="select name from panchayats where blockCode='%s' and panchayatCode='%s'" % (blockCode,panchayatCode)
    panchayatName=singleRowQuery(cur,query)
    phone='0'
 
  jobcardListForm=gotoJobcardListForm(blockCode,panchayatCode,'Go Back To Jobcard List')
  myhtml+= '<br />' + getCenterAligned('<h5 style="color:blue">Block [%s] </h5>' % blockName)
  myhtml+=  getCenterAligned('<h5 style="color:blue">Panchayat [%s] </h5>' % panchayatName)
  myhtml+= '<br /> <br />' + getCenterAligned('<h5 style="color:blue">Update Phone Number</h5>' )
  myform=getPhoneUpdateForm(blockCode,panchayatCode,blockName,panchayatName,jobcard,phone) 
  myhtml+=myform
  myhtml+=getCenterAligned(jobcardListForm)

  #myhtml+= '<br />' + getCenterAligned('<h5>Return to the <a href="./queryDashboard.py">Query Dashboard</a></h5>')

  myhtml=htmlWrapper(title="Update Address Book", head='<h1 align="center">Update Phone Number</h1>', body=myhtml)
  print myhtml.encode('UTF-8')
if __name__ == '__main__':
  main()
