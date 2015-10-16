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
  myhtml+=  getCenterAligned('<h3 style="color:green"><a href="http://ap.libtech.info/broadcasts/ui/html/broadcastsMain.html">Broadcast Management System </a></h3>' )
  myhtml+="</br>"
  myhtml+=  getCenterAligned('<h3 style="color:green"><a href="http://ap.libtech.info/ghattuGrievance/ghattu/nrega/html/">Grievance Management System </a></h3>' )
  myhtml+="</br>"
  myhtml=htmlWrapper(title="AP Telangana Dashboard", head='<h1 align="center">AP Telangana Dashboard</h1>', body=myhtml)
  print myhtml.encode('UTF-8')
if __name__ == '__main__':
  main()
