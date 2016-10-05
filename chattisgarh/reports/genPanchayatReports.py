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
from libtechFunctions import singleRowQuery,writecsv
from globalSettings import datadir,nregaDataDir,reportsDir,nregaStaticReportsDir
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIQuery2HTML
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
def genReport(cur,logger,isBlock,htmlDir,finyear,districtName,blockCode,blockName,panchayatCode,panchayatName):
  blockFilterQuery=" and b.blockCode="+str(blockCode)
  panchayatFilterQuery=" and p.panchayatCode="+str(panchayatCode)
  pdir=panchayatName.upper()+'/'
  if isBlock == 1:
    panchayatFilterQuery=''
    panchayatCode=''
    panchayatName=''
    pdir=''
  logger.info("Processing"+blockName+panchayatName) 
  query="select title,dbname,selectClause,whereClause,orderClause,dbname,groupClause,linkIndex,linkType,limitResults,finyearFilter from reportQueries" 
  cur.execute(query)
  queryResults=cur.fetchall()
  for queryRow in queryResults:
    title=queryRow[0]
    dbname=queryRow[1]
    selectClause=queryRow[2]
    whereClause=queryRow[3]
    orderClause=queryRow[4]
    groupClause=queryRow[6]
    limit=queryRow[9]
    limitString=" limit 200 "
    if limit ==0:
      limitString=''
    finyearFilter=queryRow[10]
    if finyear == 'all':
      rdir="REPORTS"
      finyearFilterQuery=""
    else:
      finyearFilterQuery=finyearFilter.replace("myfinyear",finyear)
      rdir="REPORTS"+finyear
    if groupClause is None:
      query=selectClause+" where "+whereClause+blockFilterQuery+panchayatFilterQuery+finyearFilterQuery+"  order by  "+orderClause+limitString
    else: 
      query=selectClause+" where "+whereClause+blockFilterQuery+panchayatFilterQuery+finyearFilterQuery+" group by "+groupClause+"  order by  "+orderClause+limitString
    #queryWithoutLimit=query.replace("limit 50"," ")
    if queryRow[7] and queryRow[8]:
      linkIndex=queryRow[7].split(',')
      linkType=queryRow[8].split(',')
      logger.info(query)
      queryTable=tabletUIQuery2HTML(cur,query,hiddenValues=linkIndex,hiddenNames=linkType,districtName=districtName,blockName=blockName,panchayatName=panchayatName)
    else:
      queryTable=tabletUIQuery2HTML(cur,query)
    queryTable=queryTable.replace('query_text',query) 
    myhtml=''
    myhtml+=  getCenterAligned('<h2 style="color:blue"> %s</h2>' % (title))
    myhtml+=  getCenterAligned('<h3 style="color:green"> %s-%s</h3>' % (blockName.upper(),panchayatName.upper()))
    
    myhtml+= queryTable
  
    curhtmlfile=htmlDir+districtName.upper()+"/"+blockName.upper()+"/"+pdir+rdir+"/"+title.replace(' ','')+".html"
    logger.info(curhtmlfile)
    myhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">Reports Page</h1>', body=myhtml)
    if not os.path.exists(os.path.dirname(curhtmlfile)):
      os.makedirs(os.path.dirname(curhtmlfile))
    f=open(curhtmlfile,'w')
    f.write(myhtml.encode("UTF-8"))
    query=selectClause+" where "+whereClause+blockFilterQuery+panchayatFilterQuery+finyearFilterQuery+"  order by  "+orderClause
    logger.info(query)
    curcsvfile=htmlDir+districtName.upper()+"/"+blockName.upper()+"/"+pdir+rdir+"/"+title.replace(' ','')+".csv"
    writecsv(cur,query,curcsvfile)
 
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

  htmlDir=nregaStaticReportsDir.replace("districtName",districtName.lower())

  #block Reports
  query="select b.name,b.blockCode from blocks b where b.isRequired=1"
  #query="select b.name,b.blockCode from blocks b where b.isRequired=1 limit 1"
  #query="select b.name,b.blockCode,p.name,p.panchayatCode from panchayats p, blocks b where b.blockCode=p.blockCode and p.isRequired=1 limit 1"
  #query="select b.name,b.blockCode,p.name,p.panchayatCode from panchayats p, blocks b where b.blockCode=p.blockCode and p.isRequired=1 and b.blockCode='005' "
#  query="select b.name,b.blockCode,p.name,p.panchayatCode from panchayats p, blocks b where b.blockCode=p.blockCode and p.isRequired=1 and b.blockCode='003' and panchayatCode='013'"
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    blockName=row[0]
    blockCode=row[1]
    genReport(cur,logger,1,htmlDir,'16',districtName,blockCode,blockName,'','') 
    genReport(cur,logger,1,htmlDir,'17',districtName,blockCode,blockName,'','') 
    genReport(cur,logger,1,htmlDir,'all',districtName,blockCode,blockName,'','') 
 
  query="select b.name,b.blockCode,p.name,p.panchayatCode from panchayats p, blocks b where b.blockCode=p.blockCode and p.isRequired=1"
  #query="select b.name,b.blockCode,p.name,p.panchayatCode from panchayats p, blocks b where b.blockCode=p.blockCode and p.isRequired=1 limit 1"
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    blockName=row[0]
    blockCode=row[1]
    panchayatName=row[2]
    panchayatCode=row[3]
    finyear='16'
    genReport(cur,logger,0,htmlDir,'16',districtName,blockCode,blockName,panchayatCode,panchayatName) 
    genReport(cur,logger,0,htmlDir,'17',districtName,blockCode,blockName,panchayatCode,panchayatName) 
    genReport(cur,logger,0,htmlDir,'all',districtName,blockCode,blockName,panchayatCode,panchayatName) 

  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()
