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


def main():
  print 'Content-type: text/html'
  print
  form = cgi.FieldStorage()
  requestType=form['formType'].value
  rowid = form['rowid'].value
  db = dbInitialize(host=pdsDBHost,db=pdsDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  myhtml=''
  myhtml+='<h2><a href="http://callmgr.libtech.info/auth/broadcastUI/python/pdsBroadcastApprove.py" > Go back to PDS List </a></h2>' 
  query="update fpsStatus set initiateBroadcast=1,initiateBroadcastDate=NOW() where id=%s" % rowid
  cur.execute(query)
  query="select f.districtName,f.blockName,f.fpsName,f.totalNumbers,fs.month,fs.year from fpsShops f,fpsStatus fs where fs.fpsCode=f.fpsCode and fs.id=%s" % rowid
  queryTable= bsQuery2HtmlV2(cur, query)
  myhtml+=queryTable
  myhtml=htmlWrapperLocal(title="Broadcast Scheduled", head='<h1 aling="center">Broadcast Scheduled</h1>', body=myhtml)
  print myhtml.encode("UTF-8")

if __name__ == '__main__':
  main()
