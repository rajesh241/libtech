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
from processBroadcasts import getGroupQueryMatchString,getLocationQueryMatchString 
from settings import dbhost,dbuser,dbpasswd,sid,token
from libtechFunctions import gethtmlheader 
from libtechFunctions import gethtmlfooter 
from libtechFunctions import singleRowQuery,arrayToHTMLLine,writecsv 
from globalSettings import broadcastsReportFile,broadcastReportFilePath
def getform(bid,formtype,inputElement,buttonText):
  formhtml='<br /><form action="./approveBroadcastPost.py" method="POST"><input name="bid" value="%s" type="hidden"><input name="formType" value="%s" type="hidden"></input>%s<button type="submit">%s</button></form>' %(bid,formtype,inputElement,buttonText)
  return formhtml

def dropdownOptionSet(html, str):
  '''
  Sets the option as selected for the chosen dropdown
  '''
  if str != "":
    old_str = '<option value="' + str + '">'
    new_str = old_str.replace('">', '" selected>')
    return html.replace(old_str, new_str)
  else:
    return html


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
  #print "Printing Broadcast reports"
  myhtml=gethtmlheader()
  myhtml+="<h1>Approve Broadcasts Page</h1>"
  myhtml+="<p>Please be careful in approving Broadcasts. If you have selected vendor as 'any' then you need to do seperate test with both exotel and tringo. Or if you have selected broadcast for specific vendor, then you can do the test only with that vendor. Once you successfully receive the callback, go ahead and press the approve button."
  myhtml+="<table>"
  tableArray=['Broadcast ID', 'Broadcast Name','Test','Remarks','Approve','Mark Error'] 
  myhtml+=arrayToHTMLLine('th',tableArray)
 # print myhtml
  query="select bid,name,type,groups,district,blocks,panchayats,vendor from broadcasts where bid>1000 and approved=0 and error=0"
  #print query
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    bid=row[0]
    name=row[1]
    vendor_value=row[7]
    vendor = '''
<select name="vendorName">
  <option value="any">Any</option>
  <option value="tringo">Tringo</option>
  <option value="exotel">Exotel</option>
</select>
    '''
    vendor = dropdownOptionSet(vendor, vendor_value)
    vendorhtml = getform(str(bid),'vendor', vendor,'Update Vendor')
    
    #print "BID for Broadcast is "+str(bid)
    broadcastType=row[2]
    if (broadcastType == "group"):
      #Lets first get the audioFileNames
      queryMatchString=getGroupQueryMatchString(cur,row[3]) 
    elif (broadcastType == "location"):
      queryMatchString=getLocationQueryMatchString(row[4],row[5],row[6])
    else:
      queryMatchString=" district='abcd'"
      error=1
    #Additional parameters for eliminating DND numbers while selecting vendor
    if vendor_value == 'exotel':
      additionalQuery=" dnd = 'no' and "
    else:
      additionalQuery=''
    query="select count(*) from addressbook where "+additionalQuery+queryMatchString+" "
    #print query
    cur.execute(query)
    row1=cur.fetchone()
    notes=str(row1[0])+" calls will be scheduled"


   # print "Current Bid is"+str(bid)
    #updateBroadcastTable(cur,bid)
    formElement = '<input name="phone" type="text" size="10" ></input>'
    exotelhtml=getform(str(bid),'exotel',formElement,'Test')
#    tringohtml=getform(str(bid),'tringo',formElement,'Test Tringo')
    approvehtml=getform(str(bid),'approve',' ','Approve')
    errorhtml=getform(str(bid),'error',' ','Mark Error')
    tableArray=[bid,name,exotelhtml,notes,approvehtml,errorhtml] 
    myhtml+=arrayToHTMLLine('td',tableArray)
    #write csv report
  myhtml+="</table>"
  myhtml+=gethtmlfooter()
  print myhtml

if __name__ == '__main__':
  main()
