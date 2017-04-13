#!/usr/bin/python
import cgi
import cgitb; cgitb.enable() # Optional; for debugging only
import MySQLdb
import os
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../../includes/')
sys.path.insert(0, fileDir+'/../../../')
sys.path.insert(0, fileDir+'/../../../pds/scripts/')
#sys.path.insert(0, rootdir)
from bootstrap_utils import bsQuery2HtmlV2,getButtonV2,htmlWrapperLocal
from wrappers.db import dbInitialize,dbFinalize
from pdsFunctions import cleanFPSName,writeFile
from pdsSettings import pdsDB,pdsDBHost,pdsRawDataDir,pdsWebDirRoot,pdsUIDir,pdsAudioDir

def genWebReport():
  db = dbInitialize(host=pdsDBHost,db=pdsDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
 
  myhtml=''
  query="select fs.id,f.districtName,f.blockName,f.fpsName,f.village,fs.year,fs.month,DATE_FORMAT(fs.deliveryDate,'%d/%m/%Y') deliveryDate,f.totalNumbers,fs.fpsCode,fs.audioPresent from fpsShops f, fpsStatus fs where f.cRequired=1 and f.fpsCode=fs.fpsCode and fs.audioPresent=1 and fs.initiateBroadcast=0 order by fs.deliveryDate DESC,fs.id DESC limit 100"
  section_html = getButtonV2('./pdsBroadcastApproveRequest.py', 'approvePDSBroadcast', 'Approve')
  hiddenNames=['rowid'] 
  hiddenValues=[0]
  #queryTable=bsQuery2Html(cur,query)
  queryTable= bsQuery2HtmlV2(cur, query, query_caption="",extraLabel='Approve',extra=section_html,hiddenNames=hiddenNames,hiddenValues=hiddenValues)
  myhtml+="<h2><a href='./fps.csv'> Download CSV </a></h2>"
  myhtml+=queryTable
  myhtml+="<h2>Broadcast Report </h2>"
  query="select fs.id,f.districtName,f.blockName,f.fpsName,f.village,fs.year,fs.month,DATE_FORMAT(fs.deliveryDate,'%d/%m/%Y') deliveryDate,f.totalNumbers,fs.fpsCode,fs.bid from fpsShops f, fpsStatus fs where f.cRequired=1 and f.fpsCode=fs.fpsCode and fs.audioPresent=1 and fs.initiateBroadcast=1 order by fs.deliveryDate DESC limit 100"
  queryTable= bsQuery2HtmlV2(cur, query)
  myhtml+=queryTable
  myhtml=htmlWrapperLocal(title="PDS Report", head='<h1 aling="center">Panchayats Reports</h1>', body=myhtml)
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  return myhtml

def main():
  print 'Content-type: text/html'
  print
  myhtml=genWebReport() 
  print myhtml

if __name__ == '__main__':
  main()
