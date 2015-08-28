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
import libtechFunctions
import globalSettings
import settings
from globalSettings import chaupalDataSummaryReportDir,chaupalDashboardLink,chaupalDataDashboardLink,chaupalDataDashboardLimit
from settings import dbhost,dbuser,dbpasswd,sid,token
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapper, getForm, getButton, getButtonV2,getCenterAligned
def genHTMLFile(cur,query,heading,htmlFile,extrahtml=None):
  myhtml=''
  if extrahtml is not None:
   myhtml+=extrahtml
  query_table = "<br />"
  query_table += bsQuery2HtmlV2(cur, query)
  myhtml +=query_table
  f = open(htmlFile, 'w')
  myhtml=htmlWrapper(title=heading, head='<h1 aling="center">'+heading+'</h1>', body=myhtml)
  f.write(myhtml.encode("UTF-8"))
def genQueryTable(cur,query,heading):
  myhtml=''
  query_table = "<br />"
  query_table += bsQuery2HtmlV2(cur, query)
  myhtml +=query_table
  return myhtml

def main():
  print 'Content-type: text/html'
  print
  myhtml='' 
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use surguja"
  cur.execute(query)
  queryType='data'
  query="select id,title,query from reportQueries where type='%s' order by id desc" % queryType
  cur.execute(query)
  queries=cur.fetchall()
  for row in queries:
    query=row[2]+" limit "+str(chaupalDataDashboardLimit)
    title=row[1]
    myhtml+= getCenterAligned('<h5 style="color:blue">%s</h5>'% title)
    myhtml+=genQueryTable(cur,query,title)
  htmlFile=chaupalDataSummaryReportDir +'index.html'
  f = open(htmlFile, 'w')
  myhtml=htmlWrapper(title="Chaupal Data Dashboard", head='<h1 aling="center">Chaupal Data Dashboard</h1>', body=myhtml)
  f.write(myhtml.encode("UTF-8"))
# chaupalDashboardHTML =  getCenterAligned('<h5 style="color:blue"><a href="%s">Go back to Main Chaupal Dashboard</a></h5>'%  chaupalDashboardLink )
# chaupalDataDashboardHTML =  '</br>'+getCenterAligned('<h5 style="color:green"><a href="%s">Go back Data Dashboard</a></h5>'%  chaupalDataDashboardLink )
# extrahtml=chaupalDashboardHTML+chaupalDataDashboardHTML
#Generate Latest Musters File
# query="select b.name block, p.name panchayat, m.musterNo, m.workName, DATE_FORMAT(m.dateFrom,'%d-%m-%Y') FromDate, DATE_FORMAT(m.dateTo,'%d-%m-%Y') ToDate from musters m, blocks b, panchayats p where b.blockCode=m.blockCode  and m.blockCode=p.blockCode and m.panchayatCode=p.panchayatCode order by m.crawlDate DESC,m.dateFrom DESC limit 50"
# htmlFile=chaupalDataSummaryReportDir+'latestMusters.html'
# genHTMLFile(cur,query,'Latest Musters',htmlFile,extrahtml) 
#
# 
# myhtml+=  getCenterAligned('<h2 style="color:green">Recent Musters</h2>' )
# query="select b.name block, p.name panchayat, m.musterNo, m.workName, DATE_FORMAT(m.dateFrom,'%d-%m-%Y') FromDate, DATE_FORMAT(m.dateTo,'%d-%m-%Y') ToDate from musters m, blocks b, panchayats p where b.blockCode=m.blockCode  and m.blockCode=p.blockCode and m.panchayatCode=p.panchayatCode order by m.crawlDate DESC,m.dateFrom DESC limit 5"
# query="select b.name block,p.name panchayat, DATE_FORMAT(m.dateFrom,'%d-%m-%Y') workDate, m.workName workName,mt.name,mt.daysWorked Days,mt.totalWage wage,mt.jobcard jobcard,mt.accountNo account,DATE_FORMAT(mt.creditedDate,'%d-%m-%Y') creditedDate from musterTransactionDetails mt, musters m, blocks b, panchayats p where b.blockCode=mt.blockCode and p.blockCode=mt.blockCode and p.panchayatCode=mt.panchayatCode and mt.blockCode=m.blockCode and mt.musterNo=m.musterNo order by mt.creditedDate DESC limit 5;"
# query_table = "<br />"
# query_table += bsQuery2HtmlV2(cur, query)
# myhtml +=query_table
# myhtml += getCenterAligned('<a href="%s"><h5>View Full Details</h5></a></div>' % './latestMusters.html') + '<br />'
# 

if __name__ == '__main__':
  main()
