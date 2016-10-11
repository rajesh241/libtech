from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
import time
import re
import sys
from MySQLdb import OperationalError
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
sys.path.insert(0, fileDir+'/../scripts/')
from crawlFunctions import getDistrictParams
#sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery,writeFile
from globalSettings import datadir,nregaDataDir,reportsDir,nregaDir
from nregaSettings import nregaWebDir,nregaRawDataDir 
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocalRelativeCSS, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable
#from crawlSettings import crawlIP,stateName,stateCode,stateShortCode,districtCode
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Generate Reports for Districts')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-d', '--district', help='Please enter the district', required=True)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  if args['district']:
    districtName=args['district'].lower()
  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  
  htmlDir=nregaDir.replace("districtName",districtName.lower())
  logger.info(htmlDir)

  #Generate District Level UI
  curhtmlfile=htmlDir+"/index.html"
  logger.info(curhtmlfile)
  query="use crawlDistricts"
  cur.execute(query)
  query="select name from districts limit 1"
  myhtml=""
  myhtml+=tabletUIQueryToHTMLTable(cur,query) 
  myhtml=htmlWrapperLocalRelativeCSS(title="Select District", head='<h1 aling="center">Select District</h1>', body=myhtml)
 # writeFile(curhtmlfile,myhtml)
  cur.execute(query)
  distResults=cur.fetchall()
  for distRow in distResults:
    districtName=distRow[0]
    crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)
    htmlDir=nregaWebDir.replace("stateName",stateName.upper()).replace("districtName",districtName.upper())
    query="use %s " % districtName.lower()
    logger.info(query)
    cur.execute(query) 
   
   
    disthtmlfile=htmlDir+districtName.upper()+".html"
    logger.info(disthtmlfile)
    query="select name from blocks where isRequired=1"
    myhtml=tabletUIQueryToHTMLTable(cur,query) 
    myhtml=htmlWrapperLocalRelativeCSS(relativeCSSPath='.',title="Block Page", head='<h1 aling="center">'+districtName.upper()+'</h1>', body=myhtml)
    writeFile(disthtmlfile,myhtml)
    
   #Generate Block Level Pages
    query="select name,blockCode from blocks where isRequired=1 order by name"
    cur.execute(query)
    results=cur.fetchall()
    for row in results:
      blockName=row[0]
      blockCode=row[1]
      h1title=districtName.upper()+"-"+blockName
      curhtmlfile=htmlDir+districtName.upper()+"/"+blockName.upper()+"/"+blockName.upper()+".html"
    
      #Lets print a block Level Reports Page
      myhtml=""
      query="select name from panchayats where blockCode='%s' and isRequired=1 order by name" %(blockCode) 
      myhtml+=tabletUIQueryToHTMLTable(cur,query) 
      query="select id,title from reportQueries where isRequired=1"
      logger.info(query)
      myhtml+=tabletUIReportTable(cur,query,staticLinkPath="REPORTS") 
      myhtml=htmlWrapperLocalRelativeCSS(relativeCSSPath='../',title="Panchayats Page", head='<h1 aling="center">'+h1title+'</h1>', body=myhtml)
      #writeFile(curhtmlfile,myhtml)
    #Generate Panchayat Level Page
   #Generate Panchayat Level Page
    query="select b.name,b.blockCode,p.name,p.panchayatCode from panchayats p, blocks b where b.blockCode=p.blockCode and p.isRequired=1 order by p.name"
    cur.execute(query)
    results=cur.fetchall()
    for row in results:
      blockName=row[0]
      blockCode=row[1]
      panchayatName=row[2]
      panchayatNameOnlyLetters=re.sub(r"[^A-Za-z]+", '', panchayatName)
      panchayatCode=row[3]
      h1Title=districtName.upper()+"-"+blockName+"-"+panchayatName.upper()
      curhtmlfile=htmlDir+districtName.upper()+"/"+blockName.upper()+"/"+panchayatNameOnlyLetters.upper()+"/"+panchayatNameOnlyLetters.upper()+".html"
      logger.info(curhtmlfile)
      query="select id,title from reportQueries where isRequired=1"
      myhtml=tabletUIReportTable(cur,query,staticLinkPath="REPORTS") 
      myhtml=htmlWrapperLocalRelativeCSS(relativeCSSPath='../../',title="Reports Page", head='<h1 aling="center">'+h1Title+'</h1>', body=myhtml)
      #writeFile(curhtmlfile,myhtml)
       
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()
