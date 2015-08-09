import os
import logging
import MySQLdb
import time
import requests
import datetime
import xml.etree.ElementTree as ET
import re
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
import libtechFunctions
import globalSettings
import settings
from settings import dbhost,dbuser,dbpasswd,sid,token
from libtechFunctions import getjcNumber,singleRowQuery
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
  query="select blockCode,panchayatCode,name from panchayats " 
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    blockCode=row[0]
    panchayatCode=row[1]
    panchayatName=row[2]
    query="select name from blocks where blockCode='%s'" % blockCode
    blockName=singleRowQuery(cur,query)
    query="select count(*) from jobcardRegister where blockCode='%s' and panchayatCode='%s'" % (blockCode,panchayatCode)
    totalJobcards=str(singleRowQuery(cur,query))
    jcMatch="%CH-05-"+blockCode+"-"+panchayatCode+"-%"
    query="select count(*) from jobcardDetails where jobcard like '%s' " % (jcMatch)
    print query
    totalWorkers=str(singleRowQuery(cur,query))
    query="use libtech"
    cur.execute(query)
    query="select count(*) from addressbook where district='surguja' and block='%s' and panchayat='%s'" % (blockName.lower(),panchayatName.lower())
    totalMoblies=str(singleRowQuery(cur,query))
    print blockName+"  "+panchayatName+"  "+totalJobcards+"  "+totalWorkers
    query="use surguja"
    cur.execute(query)
    query="update panchayats set totalJobcards=%s,totalWorkers='%s',totalMobiles='%s' where panchayatCode='%s' and blockCode='%s'" % (totalJobcards,totalWorkers,totalMoblies,panchayatCode,blockCode)
    print query
    cur.execute(query)

if __name__ == '__main__':
  main()
