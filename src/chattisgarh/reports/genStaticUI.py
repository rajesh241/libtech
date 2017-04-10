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
#sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery
from globalSettings import datadir,nregaDataDir,reportsDir,nregaStaticReportsDir
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable
from crawlSettings import crawlIP,stateName,stateCode,stateShortCode,districtCode

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='HouseKeeping Script for SurGUJA Database')
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

  query="use %s " % districtName.lower()
  cur.execute(query)
  htmlDir=nregaStaticReportsDir.replace("districtName",districtName.lower())
  logger.info(htmlDir)
  myhtml='<h1>Welcome to %s DATA Dashboard </h1><h2><a href="./reports/">Go to Districts </a><h2>' % stateName
  indexfile=htmlDir+"/../index.html"
  if not os.path.exists(os.path.dirname(indexfile)):
    os.makedirs(os.path.dirname(indexfile))
  f=open(indexfile,'w')
  f.write(myhtml.encode("UTF-8"))
  indexfile=htmlDir+"index.html"
# query="use libtech"
# cur.execute(query)
# query="select name from crawlDistricts where state='%s' and name='%s'" %(stateName,districtName.lower())
# myhtml=tabletUIQueryToHTMLTable(cur,query) 
# myhtml=htmlWrapperLocal(title="Select Districts", head='<h1 aling="center">Select District</h1>', body=myhtml)
# logger.info(indexfile)
# if not os.path.exists(os.path.dirname(indexfile)):
#   os.makedirs(os.path.dirname(indexfile))
# f=open(indexfile,'w')
# f.write(myhtml.encode("UTF-8"))

  #Generate District Level Pages
#  query="use %s " % districtName.lower()
#  cur.execute(query)
  disthtmlfile=htmlDir+districtName.upper()+"/"+districtName.upper()+".html"
  myhtml=''
  query="select name from blocks where isRequired=1"
  myhtml=tabletUIQueryToHTMLTable(cur,query) 
  myhtml=htmlWrapperLocal(title="Block Page", head='<h1 aling="center">Select Block</h1>', body=myhtml)
  if not os.path.exists(os.path.dirname(disthtmlfile)):
    os.makedirs(os.path.dirname(disthtmlfile))
  f=open(disthtmlfile,'w')
  f.write(myhtml.encode("UTF-8"))
  
  #Generate Block Level Pages
  query="select name,blockCode from blocks where isRequired=1"
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    blockName=row[0]
    blockCode=row[1]
    h1title=districtName.upper()+"-"+blockName
    curhtmlfile=htmlDir+districtName.upper()+"/"+blockName.upper()+"/"+blockName.upper()+".html"
    #Lets print a block Level Reports Page
    myhtml=""
    query="select name from panchayats where blockCode='%s' and isRequired=1" %(blockCode) 
    myhtml+=tabletUIQueryToHTMLTable(cur,query) 
    query="select id,title from reportQueries"
    myhtml+=tabletUIReportTable(cur,query,staticLinkPath="REPORTS") 
    myhtml=htmlWrapperLocal(title="Panchayats Page", head='<h1 aling="center">'+h1title+'</h1>', body=myhtml)
    if not os.path.exists(os.path.dirname(curhtmlfile)):
      os.makedirs(os.path.dirname(curhtmlfile))
    f=open(curhtmlfile,'w')
    f.write(myhtml.encode("UTF-8"))
  #Generate Panchayat Level Page
  query="select b.name,b.blockCode,p.name,p.panchayatCode from panchayats p, blocks b where b.blockCode=p.blockCode and p.isRequired=1"
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    blockName=row[0]
    blockCode=row[1]
    panchayatName=row[2]
    panchayatCode=row[3]
    h1Title=districtName.upper()+"-"+blockName+"-"+panchayatName.upper()
    curhtmlfile=htmlDir+districtName.upper()+"/"+blockName.upper()+"/"+panchayatName.upper()+"/"+panchayatName.upper()+".html"
    logger.info(curhtmlfile)
    query="select id,title from reportQueries"
    myhtml=tabletUIReportTable(cur,query,staticLinkPath="REPORTS") 
    myhtml=htmlWrapperLocal(title="Reports Page", head='<h1 aling="center">'+h1Title+'</h1>', body=myhtml)
    if not os.path.exists(os.path.dirname(curhtmlfile)):
      os.makedirs(os.path.dirname(curhtmlfile))
    f=open(curhtmlfile,'w')
    f.write(myhtml.encode("UTF-8"))
      
     
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()
