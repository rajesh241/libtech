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
from globalSettings import datadir,nregaDataDir,reportsDir,nregaDir
from crawlFunctions import getDistrictParams
#sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery,writecsv,getFullFinYear,writeFile
from globalSettings import datadir,nregaDataDir,reportsDir,nregaStaticReportsDir
from nregaSettings import nregaStaticWebDir,nregaRawDataDir 
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocalRelativeCSS, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIQuery2HTML

def genReport(cur,logger,isBlock,htmlDir,finyear,districtName,blockCode,blockName,panchayatCode,panchayatName,reportIDFilter,jobcard):
  blockFilterQuery=" and b.blockCode="+str(blockCode)
  panchayatFilterQuery=" and p.panchayatCode="+str(panchayatCode)
  panchayatNameOnlyLetters=re.sub(r"[^A-Za-z]+", '', panchayatName)
  pdir=panchayatNameOnlyLetters.upper()+'/'
  relativeCSSPath='../../../'
  if isBlock == 1:
    panchayatFilterQuery=''
    panchayatCode=''
    panchayatName=''
    pdir=''
    relativeCSSPath='../../'
  logger.info("Processing"+blockName+panchayatName) 
  myhtml=''
  query="select title,dbname,selectClause,whereClause,orderClause,dbname,groupClause,linkIndex,linkType,limitResults,finyearFilter,jrFilter from reportQueries where jrRequired=1 %s"  % (reportIDFilter) 
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
    jrFilter=queryRow[11]
    jrFilterQuery=" and %s=%s " % (jrFilter,jobcard)
    finyearFilter=queryRow[10]
    if finyear == 'all':
      rdir="REPORTS"
      finyearFilterQuery=""
    else:
      finyearFilterQuery=finyearFilter.replace("myfinyear",finyear)
      rdir="REPORTS"+finyear
    if groupClause is None:
      query=selectClause+" where "+whereClause+jrFilterQuery+blockFilterQuery+panchayatFilterQuery+finyearFilterQuery+"  order by  "+orderClause+limitString
    else: 
      query=selectClause+" where "+whereClause+jrFilterQuery+blockFilterQuery+panchayatFilterQuery+finyearFilterQuery+" group by "+groupClause+"  order by  "+orderClause+limitString
    #queryWithoutLimit=query.replace("limit 50"," ")
    if queryRow[7] and queryRow[8]:
      linkIndex=queryRow[7].split(',')
      linkType=queryRow[8].split(',')
      logger.info(query)
      queryTable=tabletUIQuery2HTML(cur,query,hiddenValues=linkIndex,hiddenNames=linkType,districtName=districtName,blockName=blockName,panchayatName=panchayatName,isBlock=isBlock)
    else:
      queryTable=tabletUIQuery2HTML(cur,query)
    queryTable=queryTable.replace('query_text',query) 
    myhtml+=  getCenterAligned('<h2 style="color:blue"> %s</h2>' % (title))
    myhtml+=  getCenterAligned('<h3 style="color:green"> %s-%s</h3>' % (blockName.upper(),panchayatName.upper()))
    
    myhtml+= queryTable
  
  return myhtml 

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='HouseKeeping Script for SurGUJA Database')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-d', '--district', help='Please enter the district', required=True)
  parser.add_argument('-limit', '--limit', help='Limit the number of entries that need to be processed', required=False)

  args = vars(parser.parse_args())
  return args

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
  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)

  htmlDir=nregaStaticWebDir.replace("stateName",stateName.upper()).replace("districtName",districtName.upper())
  query="select b.blockCode,b.name,p.panchayatCode,p.name from blocks b, panchayats p where b.blockCode=p.blockCode and p.isRequired=1  %s " % (limitString)
    #query="select b.blockCode,b.name,p.panchayatCode,p.name from blocks b, panchayats p where b.blockCode=p.blockCode and p.isRequired=1 and b.blockCode='003' "
  cur.execute(query)
  panchResults=cur.fetchall()
  for panchRow in panchResults:
    blockCode=panchRow[0]
    blockName=panchRow[1]
    panchayatCode=panchRow[2]
    panchayatName=panchRow[3]
    logger.info("Processing blockCode: %s blockName: %s panchayatCode: %s PanchayatName: %s " %(blockCode,blockName,panchayatCode,panchayatName))
    
    query="select jobcard from jobcardRegister where blockCode='"+blockCode+"' and panchayatCode='"+panchayatCode+"' " 
    cur.execute(query)
    results=cur.fetchall()
    for row in results:
      jobcard=row[0]
      logger.info(jobcard)
      jcReportFileName=htmlDir+"/"+blockName.upper()+"/"+panchayatName.upper()+"/jobcardRegister/"+jobcard.replace("/","_")+".html"
      logger.info(jcReportFileName)
      myhtml=''
      myhtml+=genReport(cur,logger,0,htmlDir,'all',districtName,blockCode,blockName,panchayatCode,panchayatName,'',jobcard) 
      myhtml=htmlWrapperLocalRelativeCSS(relativeCSSPath='../../../',title=jobcard, head='<h1 aling="center">Jobcard Register</h1>', body=myhtml)
      writeFile(jcReportFileName,myhtml)
#     myhtml='<h1>Jobcard Register</h1>' 
#     myhtml=""
#     myhtml+=  getCenterAligned('<h2 style="color:blue"> %s-%s</h2>' % (blockName.upper(),panchayatName.upper()))
#     myhtml+=  getCenterAligned('<h2 style="color:green"> %s</h2>' % (jobcard))
#
#     query="select issueDate,caste,village,isBPL,phone from jobcardRegister where jobcard='%s' " % (jobcard)
#     query_table = "<br />"
#     query_table += bsQuery2HtmlV2(cur, query, query_caption="JobcardInfo")
#     query_table=query_table.replace("query_text","Jobcard Information")
#    # myhtml+=  getCenterAligned('<h2 style="color:green">Jobcard Details</h2>' )
#     myhtml+=query_table
#      
#     query="select applicantNo,applicantName,age,gender,accountNo,primaryAccountHolder,bankNameOrPOName,branchNameOrPOAddress from jobcardDetails where jobcard='%s'" % jobcard
#     query_table = "<br />"
#     query_table += bsQuery2HtmlV2(cur, query)
#     myhtml+=  getCenterAligned('<h2 style="color:green">Family Details</h2>' )
#     query_table=query_table.replace("query_text","Family Details")
#     myhtml+=query_table
#     
# #   query="select sum(daysWorked) TotalDaysWorked,sum(totalWage) TotalWage from workDetails where jobcard='"+jobcard+"' "
# #   query_table = "<br />"
# #  
# #   query_table += bsQuery2HtmlV2(cur, query, query_caption="JddobcardInfo")
# #   query_table=query_table.replace("query_text","Work Stats")
# #   #myhtml+=  getCenterAligned('<h2 style="color:green">Work Stastics</h2>' )
# #   myhtml+=query_table
#
#     query="select finyear,name,workName,musterNo,DATE_FORMAT(dateFrom,'%d-%M-%Y') FromDate,DATE_FORMAT(dateTo,'%d-%M-%Y') ToDate,daysWorked,totalWage,accountNo,status,DATE_FORMAT(creditedDate,'%d-%M-%Y') creditedDate,rejectionReason from workDetails where jobcard='"+jobcard+"' order by dateFrom DESC" 
#     logger.info(query)
#     query_table = "<br />"
#     linkIndex=['3']
#     linkType=['muster']
#     rootPath='../../../'
#     #query_table += bsQuery2HtmlV2(cur, query, query_caption="JddobcardInfo")
#     query_table=tabletUIQuery2HTML(cur,query,hiddenValues=linkIndex,hiddenNames=linkType,districtName=districtName,blockName=blockName,panchayatName=panchayatName)
#     #myhtml+=  getCenterAligned('<h2 style="color:green">Work Details</h2>' )
#     query_table=query_table.replace("query_text","Work Details")
#     myhtml+=query_table
#     
#     query="select finyear,ftoNo,applicantName,primaryAccountHolder,accountNo,wagelistNo,processedDate,creditedAmount,status,rejectionReason from ftoTransactionDetails where jobcard='%s' order by processedDate DESC" %(jobcard)
#   #  logger.info(query)
#     query_table = "<br />"
#     linkIndex=['1']
#     linkType=['fto']
#     #query_table += bsQuery2HtmlV2(cur, query, query_caption="JddobcardInfo")
#     query_table=tabletUIQuery2HTML(cur,query,hiddenValues=linkIndex,hiddenNames=linkType,districtName=districtName,blockName=blockName,panchayatName=panchayatName)
#     #myhtml+=  getCenterAligned('<h2 style="color:green">Work Details</h2>' )
#     query_table=query_table.replace("query_text","FTO Details")
#     myhtml+=query_table
#     
#



  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()
