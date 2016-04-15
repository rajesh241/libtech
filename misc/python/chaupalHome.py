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
  myhtml=""
  myhtml+="</br></br></br></br></br>"
  myhtml+=  getCenterAligned('<h3 style="color:green"><a href="http://chaupal.libtech.info/broadcasts/ui/html/broadcastsMain.html">Broadcast Management System </a></h3>' )
  myhtml+="</br>"
  myhtml+=  getCenterAligned('<h3 style="color:blue"><a href="http://chaupal.libtech.info/addressDashboard/ui/index.py">Address Dashboard </a></h3>' )
  myhtml+="</br>"
  myhtml+=  getCenterAligned('<h3 style="color:blue"><a href="http://surguja.libtech.info/reports/">Data Dashboard </a></h3>' )
  myhtml+="</br>"
  myhtml+=  getCenterAligned('<h3 style="color:blue"><a href="http://chaupal.libtech.info/addressDashboard/ui/queryDashboard.py">Query Dashboard </a></h3>' )
  myhtml+="</br>"
  myhtml+=  getCenterAligned('<h3 style="color:blue"><a href="http://libtech.info/general/Chattisgarh/PDS_REPORTS">PDS Reports </a></h3>' )
  myhtml=htmlWrapper(title="Welcome to Chaupal", head='<h1 align="center">Chaupal Home</h1>', body=myhtml)
  print myhtml.encode('UTF-8')
if __name__ == '__main__':
  main()
