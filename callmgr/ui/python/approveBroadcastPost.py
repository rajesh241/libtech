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
  myhtml=gethtmlheader()
  form = cgi.FieldStorage()
  formType=form["formType"].value
  bid=form["bid"].value
  if(formType == 'approve'):
    query="update broadcasts set approved=1 where bid="+str(bid)
    cur.execute(query)
    myhtml+='<h3>Broadcast %s Approved</h3>' %(str(bid))
  elif(formType == 'error'):
    query="update broadcasts set error=1 where bid="+str(bid)
    cur.execute(query)
    myhtml+='<h3>Broadcast %s has been market as Error</h3>' %(str(bid))
  elif(formType == 'vendor'):
    vendor = form["vendorName"].value
    query="update broadcasts set vendor='" + vendor + "' where bid=" +  str(bid)
    cur.execute(query)
    myhtml+='<h3>Vendor has been updated for %s</h3>' %(str(bid))
  else:
    phone=form["phone"].value
    query="select fileid,tfileid,fileid2,template from broadcasts where bid="+str(bid)
    cur.execute(query)
    result=cur.fetchone()
    fileid=result[0]
 #   fileid1=result[2]
    template=result[3]
    tfileid=result[1]
    tringoaudio=gettringoaudio(tfileid)
    audio,error=getaudio(cur,fileid)
  #  audio1,error1=getaudio(cur,fileid1)
    if(error == 0):
      #print audio+tringoaudio 
      minhour='6'
      maxhour='23'
      exophone='02233814264'
      vendor=formType
      query="insert into callQueue (isTest,priority,vendor,bid,minhour,maxhour,phone,audio,audio1,template,tringoaudio,exophone) values (1,20,'"+vendor+"',"+str(bid)+","+minhour+","+maxhour+",'"+phone+"','"+audio+"','"+audio+"','"+template+"','"+tringoaudio+"','"+exophone+"');"
      print query 
      cur.execute(query)
      myhtml+="<h3>Test Call Placed on number %s</h3>" %(phone)
      myhtml+="<p>Please Note that it may take about 5-10 minutes to get the test call based on system load. Please sit back and relax for sometime and ensure that your phone is not on silent</p>"
    else:
      print "<h4> Some error has occured. Probably the fileID is not correct</h4>";
  #myhtml+="<h1> Thank You for Doing %s</h1>" %(formType) 
  myhtml+='<h3><a href="./approveBroadcast.py"> Return to Approve Broadcast Page</a></h3>'
  myhtml+='<h3><a href="./../html/broadcastsMain.html"> Return to Main Broadcast Page </a></h3>'
  myhtml+=gethtmlfooter()
  print myhtml
if __name__ == '__main__':
  main()
