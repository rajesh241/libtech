from bs4 import BeautifulSoup
import multiprocessing, time
import requests
import MySQLdb
import os
import os.path
import time
import re
import sys
from MySQLdb import OperationalError
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
#sys.path.insert(0, rootdir)
import datetime
from wrappers.logger import loggerFetch
from wrappers.db import dbInitialize,dbFinalize
from crawlSettings import nregaDB 
from crawlSettings import nregaWebDir,nregaRawDataDir,nregaWebDirRoot
from crawlFunctions import  tabletUIQueryToHTMLTable,htmlWrapperLocal,tabletUIReportTable
from crawlFunctions import alterHTMLTables,writeFile,getjcNumber,NICToSQLDate,getFullFinYear
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing musters')
  args = vars(parser.parse_args())
  return args
 

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))

  db = dbInitialize(db=nregaDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)

#Generate Index Level page
  curhtmlfile=nregaWebDirRoot+"/index.html"
  query="select stateName from districts group by stateName"
  myhtml=""
  myhtml+=tabletUIQueryToHTMLTable(cur,query) 
  myhtml=htmlWrapperLocal(title="Select State", head='<h1 aling="center">Select State</h1>', body=myhtml)
  writeFile(curhtmlfile,myhtml)

#Generate State Level page
  query="select stateName from districts group by stateName"
  cur.execute(query)
  results=cur.fetchall()
  for row in results: 
    stateName=row[0]
    query="select rawDistrictName from districts where stateName='%s' " % stateName
    curhtmlfile=nregaWebDirRoot+"%s/%s.html" % (stateName.upper(),stateName.upper())
    logger.info(query)
    logger.info(curhtmlfile)
    myhtml=""
    myhtml+=tabletUIQueryToHTMLTable(cur,query) 
    myhtml=htmlWrapperLocal(title="Select District", head='<h1 aling="center">Select District</h1>', body=myhtml)
    writeFile(curhtmlfile,myhtml)

#Generate District Level Level page
  query="select stateCode,districtCode,stateName,districtName from districts"
  cur.execute(query)
  results=cur.fetchall()
  for row in results: 
    stateCode=row[0]
    districtCode=row[1]
    stateName=row[2]
    districtName=row[3]
    query="select blockName from blocks where stateCode='%s' and districtCode='%s' " % (stateCode,districtCode)
    curhtmlfile=nregaWebDirRoot+"%s/%s/%s.html" % (stateName.upper(),districtName.upper(),districtName.upper())
    myhtml=""
    myhtml+=tabletUIQueryToHTMLTable(cur,query) 
    myhtml=htmlWrapperLocal(title="Select block", head='<h1 aling="center">Select Block</h1>', body=myhtml)
    writeFile(curhtmlfile,myhtml)

#Generate Block Level Level page
  query="select stateCode,districtCode,blockCode,stateName,districtName,blockName from blocks"
  cur.execute(query)
  results=cur.fetchall()
  for row in results: 
    stateCode=row[0]
    districtCode=row[1]
    blockCode=row[2]
    stateName=row[3]
    districtName=row[4]
    blockName=row[5]
    query="select panchayatName from panchayats where isRequired=1 and stateCode='%s' and districtCode='%s' and blockCode='%s'" % (stateCode,districtCode,blockCode)
    curhtmlfile=nregaWebDirRoot+"%s/%s/%s/%s.html" % (stateName.upper(),districtName.upper(),blockName.upper(),blockName.upper())
    myhtml=""
    myhtml+=tabletUIQueryToHTMLTable(cur,query) 
    query="select id,title from dashboardQueries where isRequired=1 and type='location'"
    myhtml+=tabletUIReportTable(cur,query,staticLinkPath="REPORTS") 
    myhtml=htmlWrapperLocal(title="Select Panchayats", head='<h1 aling="center">Select Panchayats</h1>', body=myhtml)
    writeFile(curhtmlfile,myhtml)

#Generate Block Level Level page
  query="select stateCode,districtCode,blockCode,stateName,districtName,blockName,panchayatCode,panchayatName from panchayats where isRequired=1"
  cur.execute(query)
  results=cur.fetchall()
  for row in results: 
    stateCode=row[0]
    districtCode=row[1]
    blockCode=row[2]
    stateName=row[3]
    districtName=row[4]
    blockName=row[5]
    panchayatCod=row[6]
    panchayatName=row[7]
    curhtmlfile=nregaWebDirRoot+"%s/%s/%s/%s/%s.html" % (stateName.upper(),districtName.upper(),blockName.upper(),panchayatName.upper(),panchayatName.upper())
    myhtml=""
   # myhtml+=tabletUIQueryToHTMLTable(cur,query) 
    query="select id,title from dashboardQueries where isRequired=1 and type='location'"
    myhtml+=tabletUIReportTable(cur,query,staticLinkPath="REPORTS") 
    myhtml=htmlWrapperLocal(title="Panchayat Reports", head='<h1 aling="center">Panchayats Reports</h1>', body=myhtml)
    writeFile(curhtmlfile,myhtml)




  dbFinalize(db) # Make sure you put this if there are other exit paths or errors

if __name__ == '__main__':
  main()
