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
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'./')
import libtechFunctions
import globalSettings
import settings
from settings import dbhost,dbuser,dbpasswd,sid,token
from libtechFunctions import singleRowQuery,scheduleTransactionCall
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
  info=form["info"].value
  phoneArray=info.split(",")
  myhtml=""
  for phone in phoneArray:
    phoneLast10=phone[-10:]
    query="select * from ghattuMissedCalls where (TIMESTAMPDIFF(HOUR, ctime, now()) < 720) and phone='%s';" % phoneLast10
    myhtml+= '<br />' + getCenterAligned('<h5 style="color:blue"> %s</h5>' % query)
    cur.execute(query)
    if (cur.rowcount == 0):
      query="insert into ghattuMissedCalls (phoneraw,phone,ctime) values ('%s','%s',NOW());" % (phone,phoneLast10)
      cur.execute(query)
      scheduleTransactionCall(cur,'1139',phone)
    myhtml+= '<br />' + getCenterAligned('<h5 style="color:blue">Ghattu Missed Calls %s</h5>' % phone)

  #myhtml+= '<br />' + getCenterAligned('<h5>Return to the <a href="./queryDashboard.py">Query Dashboard</a></h5>')

  myhtml=htmlWrapper(title="Ghattu Missed Cal Sysatem", head='<h1 align="center">Ghattu Missed Call Sysatem</h1>', body=myhtml)
  print myhtml.encode('UTF-8')
if __name__ == '__main__':
  main()
