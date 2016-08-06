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
from globalSettings import datadir,nregaDataDir,reportsDir,nregaDir,nregaArchiveDir,packageDir,cssPath
from crawlFunctions import getDistrictParams
#sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery,writecsv,getFullFinYear,writeFile
from globalSettings import datadir,nregaDataDir,reportsDir,nregaStaticReportsDir
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocalRelativeCSS, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIQuery2HTML
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocalRelativeCSS, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable


def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='HouseKeeping Script for SurGUJA Database')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-d', '--district', help='Please enter the district', required=True)
  parser.add_argument('-rid', '--reportID', help='Report ID for the report to be generated', required=False)
  parser.add_argument('-limit', '--limit', help='Limit the number of entries that need to be processed', required=False)

  args = vars(parser.parse_args())
  return args

def createPackage(cur,districtName,logger):
  htmlDir=packageDir 
  districtDir="%s/%s/" % (htmlDir,districtName.upper())
  cmd="rm -rf %s/* " % htmlDir
  os.system(cmd)
  cmd="mkdir -p %s/css " % districtDir 
  os.system(cmd)
  logger.info(cmd)
  cmd="cp -R %s/css/* %s/css" % (cssPath,districtDir)
  logger.info(cmd)
  os.system(cmd)
  disthtmlfile=htmlDir+districtName.upper()+"/"+districtName.upper()+".html"
  logger.info(disthtmlfile)
  query="select name from blocks where currentZip=1 order by name"
  myhtml=tabletUIQueryToHTMLTable(cur,query) 
  myhtml=htmlWrapperLocalRelativeCSS(relativeCSSPath='.',title="Block Page", head='<h1 aling="center">'+districtName.upper()+'</h1>', body=myhtml)
  writeFile(disthtmlfile,myhtml)
  
 #Generate Block Level Pages
  query="select name,blockCode from blocks where currentZip=1"
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    blockName=row[0]
    blockCode=row[1]
    h1title=districtName.upper()+"-"+blockName
    curhtmlfile=htmlDir+districtName.upper()+"/"+blockName.upper()+"/"+blockName.upper()+".html"
  
    #Lets print a block Level Reports Page
    myhtml=""
    query="select name from panchayats where blockCode='%s' and currentZip=1 order by name" %(blockCode) 
    myhtml+=tabletUIQueryToHTMLTable(cur,query) 
    query="select id,title from reportQueries where isRequired=1"
    logger.info(query)
    myhtml+=tabletUIReportTable(cur,query,staticLinkPath="REPORTS") 
    myhtml=htmlWrapperLocalRelativeCSS(relativeCSSPath='../',title="Panchayats Page", head='<h1 aling="center">'+h1title+'</h1>', body=myhtml)
    #Lets copy the block Reports
    webBlockDir=nregaDir+districtName.upper()+"/"+blockName.upper()+"/"
    curBlockDir=htmlDir+districtName.upper()+"/"+blockName.upper()+"/"
    cmd="mkdir -p %s " % curBlockDir
    logger.info(cmd)
    os.system(cmd)
    cmd="cp -R %s/* %s/" % (webBlockDir,curBlockDir) 
    logger.info(cmd)
    os.system(cmd)
    writeFile(curhtmlfile,myhtml)

  query="select b.name,b.blockCode,p.name,p.panchayatCode from panchayats p, blocks b where b.blockCode=p.blockCode and p.currentZip=1"
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    blockName=row[0]
    blockCode=row[1]
    panchayatName=row[2]
    panchayatNameOnlyLetters=re.sub(r"[^A-Za-z]+", '', panchayatName)
    panchayatCode=row[3]
    webPanchayatDir=nregaDir+districtName.upper()+"/"+blockName.upper()+"/"+panchayatNameOnlyLetters.upper()
    curPanchayatDir=htmlDir+districtName.upper()+"/"+blockName.upper()+"/"+panchayatNameOnlyLetters.upper()
    #Copy all the panchayat Level Files
    cmd="mkdir -p %s " % curPanchayatDir
    logger.info(cmd)
    os.system(cmd)
    cmd="cp -R %s/* %s/" % (webPanchayatDir,curPanchayatDir) 
    logger.info(cmd)
    os.system(cmd)
    #We need to overWrite the Panchayat Level File
    h1Title=districtName.upper()+"-"+blockName+"-"+panchayatName.upper()
    curhtmlfile=htmlDir+districtName.upper()+"/"+blockName.upper()+"/"+panchayatNameOnlyLetters.upper()+"/"+panchayatNameOnlyLetters.upper()+".html"
    logger.info(curhtmlfile)
    query="select id,title from reportQueries where isRequired=1"
    myhtml=tabletUIReportTable(cur,query,staticLinkPath="REPORTS") 
    myhtml=htmlWrapperLocalRelativeCSS(relativeCSSPath='../../',title="Reports Page", head='<h1 aling="center">'+h1Title+'</h1>', body=myhtml)
    writeFile(curhtmlfile,myhtml)
 
def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  if args['district']:
    districtName=args['district'].lower()
  if args['limit']:
    limitString=" limit %s " % (str(args['limit']))
  else:
    limitString="  "
  if args['reportID']:
    reportIDFilter= " and id = %s " % args['reportID']
  else:
    reportIDFilter= " "
  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)
  htmlDir=packageDir 
  query="select b.name,b.blockCode from blocks b where b.isRequired=1 %s" % limitString
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    blockName=row[0]
    blockCode=row[1]
    query="update blocks set currentZip=1 where blockCode='%s'" % blockCode   
    cur.execute(query)
    query="update panchayats set currentZip=1 where blockCode='%s' " % (blockCode)
    cur.execute(query)
    createPackage(cur,districtName,logger)
    os.chdir(htmlDir)
    zipFileDir="%s/%s/" %(nregaArchiveDir,districtName.upper())
    zipName="%s/%s.zip" % (zipFileDir,blockName.upper())
    cmd="zip -r %s *" % (zipName)
    logger.info(cmd)
    os.system(cmd)
    query="update blocks set currentZip=0"
    cur.execute(query)
    query="update panchayats set currentZip=0"
    cur.execute(query)
  #Lets do this at Panchayat LEvel
  query="select b.name,b.blockCode,p.name,p.panchayatCode from panchayats p, blocks b where b.blockCode=p.blockCode and p.isRequired=1 %s" % limitString
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    blockName=row[0]
    blockCode=row[1]
    panchayatName=row[2]
    panchayatCode=row[3]
    query="update blocks set currentZip=1 where blockCode='%s'" % blockCode   
    cur.execute(query)
    query="update panchayats set currentZip=1 where blockCode='%s' and panchayatCode='%s' " % (blockCode,panchayatCode)
    cur.execute(query)
    createPackage(cur,districtName,logger)
    os.chdir(htmlDir)
    zipFileDir="%s/%s/%s/" %(nregaArchiveDir,districtName.upper(),blockName.upper())
    zipName="%s/%s.zip" % (zipFileDir,panchayatName.upper())
    cmd="zip -r %s *" % (zipName)
    logger.info(cmd)
    os.system(cmd)
    query="update blocks set currentZip=0"
    cur.execute(query)
    query="update panchayats set currentZip=0"
    cur.execute(query)


  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()
