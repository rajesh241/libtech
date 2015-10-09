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

from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapper, getForm, getButton, getButtonV3,getCenterAligned

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
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use surguja"
  cur.execute(query)
  myhtml=""
  myhtml+=  getCenterAligned('<h2 style="color:blue"> Work Names </h2>' )
  query="select b.name,p.name,m.workCode,m.workName,DATE_FORMAT(MIN(m.dateFrom),'%d-%m-%Y') startDate,DATE_FORMAT(MAX(m.dateTo),'%d-%m-%Y') LastWorkDate,w.isRecorded Recorded from musters m,blocks b,panchayats p,works w where m.finyear=w.finyear and m.workCode=w.workCode and m.finyear='16' and p.isSurvey=1 and m.blockCode=b.blockCode and m.panchayatCode=p.panchayatCode and m.blockCode=b.blockCode group by m.workCode order by w.isRecorded,m.dateFrom DESC" 
  uploadFileForm = getButtonV3('./workNameAudioUpload.php', 'uploadWorkNameAudio', 'Add Audio File')
  fileInputHTML='''

                            Select File to upload:
                                <input type="file" name="fileToUpload" id="fileToUpload">
'''
#  addNumberFormExtraInputs='<input type="hidden" name="blockCode" value="%s"><input type="hidden" name="panchayatCode" value="%s">' % (blockCode,panchayatCode)
  uploadFileForm = uploadFileForm.replace('extrainputs','extrainputs'+fileInputHTML)
  hiddenNames=['workCode'] 
  hiddenValues=[2]
  query_table = "<br />"
  query_table += bsQuery2HtmlV2(cur, query, query_caption="",extraLabel='Edit',extra=uploadFileForm,hiddenNames=hiddenNames,hiddenValues=hiddenValues)
  myhtml+=query_table
 
  myhtml=htmlWrapper(title="Record WorkNames", head='<h1 aling="center">Record WorkNames</h1>', body=myhtml)
  print myhtml.encode('UTF-8')



if __name__ == '__main__':
  main()
