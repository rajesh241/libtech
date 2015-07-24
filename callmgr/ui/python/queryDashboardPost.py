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
import processBroadcasts
from processBroadcasts import gettringoaudio,getaudio 
from settings import dbhost,dbuser,dbpasswd,sid,token
from libtechFunctions import gethtmlheader 
from libtechFunctions import gethtmlfooter 
from libtechFunctions import singleRowQuery,arrayToHTMLLine,writecsv 
from globalSettings import broadcastsReportFile,broadcastReportFilePath

from queryDashboard import queryDB,getTableHtml,htmlWrapper, getForm, getQueryTable, getCenterAligned

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
  formType=form["formType"].value
  qid=form["qid"].value
  myhtml=""

  query = ""
  if form.__contains__("query"):
    query = form["query"].value
    
  if query[0:7] != "select ":
    myhtml+= '<br />' + getCenterAligned('<h5 style="color:red"> ERROR: Tried [%s]. Only "select ...." queries allowed</h5>' % (query))
  elif(formType == 'queryMake'):
    myhtml+=getTableHtml(cur,query)
    #myhtml += getForm(0, 'queryMake', 'Go', query)
    myhtml += getForm(0, 'queryAdd', 'Add', query)
  elif(formType == 'queryAdd'):
    cur.execute('insert into queryDB (query) VALUES ("%s")' % query)
    myhtml+=getQueryTable(cur)
    myhtml+= '<br />' + getCenterAligned('<h5 style="color:green">Query [%s] Added</h5>' % query)
  elif(formType == 'queryDelete'):
    query='delete from queryDB where qid=' +  str(qid)
    cur.execute(query)
    myhtml+='<h3>Vendor has been updated for %s</h3>' %(str(bid))
  else:
    myhtml+= getCenterAligned('<h5> Error Tried %s</h5>' % (formType)) 

  myhtml+= '<br />' + getCenterAligned('<h5>Return to the <a href="./queryDashboard.py">Query Dashboard</a></h5>')

  myhtml=htmlWrapper(title="Query Dashboard", head='<h1 aling="center"><a href="./queryDashboard.py">Query Dashboard</a></h1>', body=myhtml)
  print myhtml
if __name__ == '__main__':
  main()
