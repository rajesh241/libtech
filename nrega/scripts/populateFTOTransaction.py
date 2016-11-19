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
from libtechFunctions import singleRowQuery,getjcNumber,getFullFinYear,writeFile
from nregaSettings import nregaWebDir,nregaRawDataDir 
sys.path.insert(0, fileDir+'/../crawlDistricts/')
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable

from crawlFunctions import getDistrictParams
from crawlFunctions import alterMusterHTML,getMusterPaymentDate,alterHTMLTables
from crawlFunctions import alterFTOHTML,genHTMLHeader,NICToSQLDate
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script to Populate FTO Details Table')
  parser.add_argument('-t', '--testMode', help='Script will run in TestMode', required=False,action='store_const', const=1)
  parser.add_argument('-d', '--district', help='Please enter the district', required=True)
  parser.add_argument('-af', '--additionalFilters', help='please enter additional filters', required=False)
  parser.add_argument('-f', '--finyear', help='Please enter the finyear', required=True)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit the number of entries that need to be processed', required=False)
  args = vars(parser.parse_args())
  return args
  
def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  
  if args['limit']:
    limitString=" limit %s " % (str(args['limit']))
  else:
    limitString="  "
  additionalFilter=''
  if args['district']:
    districtName=args['district'].lower()
  if args['finyear']:
    finyear=args['finyear'].lower()
  if args['additionalFilters']:
    additionalFilter=" and "+args['additionalFilters']
  
  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)

  filepath=nregaRawDataDir.replace("districtName",districtName.lower())
  modifiedFilepath=nregaWebDir.replace("stateName",stateName.upper()).replace("districtName",districtName.upper())
  fullfinyear=getFullFinYear(finyear)
  
  query="select f.id,f.ftoNo,f.blockCode,isDistrictFTO from ftoDetails f where f.isDownloaded=1  and f.finyear='%s' and f.isPopulated=0 %s %s " % (finyear,additionalFilter,limitString)
#  query="select f.id,f.ftoNo,f.blockCode,b.name from ftoDetails f,blocks b where f.isDownloaded=1 and f.blockCode=b.blockCode and f.id=4 %s " % (limitString)
  logger.info(query)
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    error=1
    rowid=str(row[0])
    ftoNo=row[1]
    blockCode=row[2]
    isDistrictFTO=row[3]
    if isDistrictFTO == 1:
      blockName=''
    else:
      query="select name from blocks where blockCode=%s " % blockCode
      cur.execute(query)
      blockrow=cur.fetchone()
      blockName=blockrow[0]

    filename=filepath+blockName.upper()+"/FTO/"+fullfinyear+"/"+ftoNo+".html"
    modifiedFilename=modifiedFilepath+blockName.upper()+"/FTO/"+fullfinyear+"/"+ftoNo+".html"
    if isDistrictFTO == 1:
      filename=filepath+"/FTO/"+fullfinyear+"/"+ftoNo+".html"
      modifiedFilename=modifiedFilepath+"/FTO/"+fullfinyear+"/"+ftoNo+".html"
    logger.info(filename)
    if (os.path.isfile(filename)):
      error=0
      matchComplete=1 
      isComplete=1
      myhtml=open(filename,'r').read()
      
      #To Rewrite wagelist HTML
      htmlHeaderLabels=["District Name","Block Name","FTO No"]
      htmlHeaderValues=[districtName,blockName,ftoNo]
      htmlHeader=genHTMLHeader(htmlHeaderLabels,htmlHeaderValues)
      outhtml=alterHTMLTables(myhtml)
      modifiedHTML=htmlHeader+outhtml
      modifiedHTML=htmlWrapperLocal(title="FTO Details", head='<h1 aling="center">'+ftoNo+'</h1>', body=modifiedHTML)
      logger.info("Modified File Name %s " % modifiedFilename)
      writeFile(modifiedFilename,modifiedHTML)


      htmlsoup=BeautifulSoup(myhtml,"html.parser")
      myspan=htmlsoup.find('span',id="ctl00_ContentPlaceHolder1_lbl_mode")
      paymentMode=myspan.text.lstrip().rstrip()
      myspan=htmlsoup.find('span',id="ctl00_ContentPlaceHolder1_lbl_acc")
      firstSignatoryDateString=myspan.text.lstrip().rstrip()
      myspan=htmlsoup.find('span',id="ctl00_ContentPlaceHolder1_lbl_acc_p2w")
      secondSignatoryDateString=myspan.text.lstrip().rstrip()
      myspan=htmlsoup.find('span',id="ctl00_ContentPlaceHolder1_lbl_cr_proc_p")
      toFinAgencyDateString=myspan.text.lstrip().rstrip()
      logger.info("First Signatory Date: %s" % firstSignatoryDateString)
      logger.info("Second Signatory Date: %s" % secondSignatoryDateString)
      logger.info("To Financial Agency Date: %s" % toFinAgencyDateString)
      logger.info("Payment Mode: %s" % paymentMode)
      
      #Now lets us find the table of individual Transactions
      tables=htmlsoup.findAll('table')
      for table in tables:
        if "Name of primary Account holder" in str(table):
          logger.info("Found the Beneficiary Table")
          alltrs=table.findAll('tr')
          if len(alltrs) == 1:
            isComplete=0
          i=0
          for tr in alltrs:
            
            i=i+1
            if "Name of primary Account holder" not in str(tr):
              col=tr.findAll('td')
              jobcard=col[1].text.lstrip().rstrip()
              referenceNo=col[2].text.lstrip().rstrip()
              transactionDateString=col[3].text.lstrip().rstrip()
              primaryAccountHolder=col[5].text.lstrip().rstrip()
              ftoAccountNo=col[7].text.lstrip().rstrip()
              ftoAmount=col[11].text.lstrip().rstrip()
              if ftoAmount=='':
                ftoAmount="NULL"
              ftoStatus=col[12].text.lstrip().rstrip()
              processedDateString=col[13].text.lstrip().rstrip()
              rejectionReason=col[15].text.lstrip().rstrip()
              ftoName=col[4].text.lstrip().rstrip()
              wagelistNo=col[6].text.lstrip().rstrip()
              if ftoStatus == '':
                isComplete=0
              
              query="select id from ftoTransactionDetails where ftoNo='%s' and referenceNo='%s'" % (ftoNo,referenceNo)
              logger.info(query)
              cur.execute(query)
              if cur.rowcount == 0:
                query="insert into ftoTransactionDetails (ftoNo,referenceNo) values ('%s','%s')" % (ftoNo,referenceNo)
                cur.execute(query)
                ftID=str(cur.lastrowid)
              else:
                row1=cur.fetchone() 
                ftID=str(row1[0])
              blockCode=jobcard[6:9] 
              query="update ftoTransactionDetails set updateWorkDetails=1,blockCode='%s',jobcard='%s',finyear='%s',applicantName='%s',primaryAccountHolder='%s',accountNo='%s',wagelistNo='%s',transactionDate=%s,processedDate=%s,status='%s',rejectionReason='%s',creditedAmount=%s where id=%s" % (blockCode,jobcard,finyear,ftoName,primaryAccountHolder,ftoAccountNo,wagelistNo,NICToSQLDate(transactionDateString),NICToSQLDate(processedDateString),ftoStatus,rejectionReason,ftoAmount,ftID)
              logger.info(query)
              cur.execute(query)
              query="update ftoTransactionDetails set firstSignatoryDate=%s,secondSignatoryDate=%s,bankProcessedDate=%s,paymentMode='%s' where id=%s " % (NICToSQLDate(firstSignatoryDateString),NICToSQLDate(secondSignatoryDateString),NICToSQLDate(toFinAgencyDateString),paymentMode,ftID)
              logger.info(query)
              cur.execute(query)
    if error==1:
      query="update ftoDetails set isDownloaded=0 where id=%s " % rowid
    else:
      query="update ftoDetails set processedDate=NOW(),isPopulated=1,isComplete=%s where id=%s" % (str(isComplete),rowid)
    logger.info(query)
    cur.execute(query)
              


  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()


