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
from crawlFunctions import alterMusterHTML,getMusterPaymentDate
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
  fullfinyear=getFullFinYear(finyear)
  
  query="select f.id,f.ftoNo,f.blockCode,b.name from ftoDetails f,blocks b where f.isDownloaded=1 and f.blockCode=b.blockCode and f.isProcessed=0 %s " % (limitString)
  logger.info(query)
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    rowid=str(row[0])
    ftoNo=row[1]
    blockCode=row[2]
    blockName=row[3]
    filename=filepath+blockName.upper()+"/FTO/"+fullfinyear+"/"+ftoNo+".html"
    logger.info(filename)
    if (os.path.isfile(filename)): 
      myhtml=open(filename,'r').read()
      error=0
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
          for tr in alltrs:
            if "Name of primary Account holder" not in str(tr):
              col=tr.findAll('td')
              jobcard=col[1].text.lstrip().rstrip()
              transactionDateString=col[3].text.lstrip().rstrip()
              primaryAccountHolder=col[5].text.lstrip().rstrip()
              ftoAccountNo=col[7].text.lstrip().rstrip()
              ftoAmount=col[11].text.lstrip().rstrip()
              ftoStatus=col[12].text.lstrip().rstrip()
              processedDateString=col[13].text.lstrip().rstrip()
              ftoName=col[4].text.lstrip().rstrip()
              wagelistNo=col[6].text.lstrip().rstrip()
              #logger.info(jobcard)
              query="select id,name from workDetails where jobcard='%s' and wagelistNo='%s' and totalWage='%s'" % (jobcard,wagelistNo,ftoAmount)
              query="select wd.id,wd.name,jd.primaryAccountHolder,jd.accountNo from workDetails wd,jobcardDetails jd where wd.accountNo=jd.accountNo and wd.jobcard=jd.jobcard and wd.jobcard='%s' and wd.wagelistNo='%s' and wd.totalWage='%s'" % (jobcard,wagelistNo,ftoAmount)
              #logger.info(query)
              cur.execute(query)
              results=cur.fetchall()
              matchStatus="Fail"
              for row1 in results:
                musterName=row1[1]
                jdPrimaryAccountHolder=row1[2].lstrip().rstrip()
                musterAccountNo=row[3]
                if ftoName.replace(" ","").lower() in musterName.replace(" ","").lower():
                  matchStatus="Success"
                  wdID=str(row1[0])
                  musterNameLatched=row1[1]
                  logger.info("name match is Successful %s %s %s" % (wdID,musterName,musterNameLatched))
                elif primaryAccountHolder == jdPrimaryAccountHolder:
                  matchStatus="Success"
                  wdID=str(row1[0])
                  musterNameLatched=row1[1]
                  logger.info("AccountHolder match is Successful %s %s %s" % (wdID,musterName,musterNameLatched))
              if matchStatus=="Success":
                 logger.info("Match Status Success %s %s %s %s" % (wdID,jobcard,musterNameLatched,ftoName))
              else:
                 logger.info("Match Status Fail %s" % query)
                


    else:
      error=1
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()

#
#import csv
#from bs4 import BeautifulSoup
#import requests
#import MySQLdb
#import time
#import re
#import os
#import sys
#fileDir=os.path.dirname(os.path.abspath(__file__))
#sys.path.insert(0, fileDir+'/../../includes/')
#from globalSettings import datadir
#from nregaSettings import nregaRawDataDir
##Error File Defination
#errorfile = open('/tmp/processFTO.log', 'a')
#sys.path.insert(0, fileDir+'/../../')
#from nregaSettings import nregaWebDir,nregaRawDataDir 
#from libtechFunctions import writeFile,getFullFinYear,singleRowQuery
##Connect to MySQL Database
#from wrappers.logger import loggerFetch
#from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
#from wrappers.db import dbInitialize,dbFinalize
#from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable
#from crawlFunctions import getDistrictParams
#from crawlFunctions import alterFTOHTML,genHTMLHeader,NICToSQLDate
#def argsFetch():
#  '''
#  Paser for the argument list that returns the args list
#  '''
#  import argparse
#
#  parser = argparse.ArgumentParser(description='Script for Downloading FTOs')
#  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
#  parser.add_argument('-limit', '--limit', help='Limit the number of ftos to be downloaded', required=False)
#  parser.add_argument('-d', '--district', help='District for which you need to Download', required=True)
#  parser.add_argument('-f', '--finyear', help='Input Financial Year', required=True)
#
#  args = vars(parser.parse_args())
#  return args
#
#def main():
#  args = argsFetch()
#  logger = loggerFetch(args.get('log_level'))
#  logger.info('args: %s', str(args))
#
#  logger.info("BEGIN PROCESSING...")
#  if args['district']:
#    districtName=args['district']
#
#  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
#  cur=db.cursor()
#  db.autocommit(True)
#  #Query to set up Database to read Hindi Characters
#  query="SET NAMES utf8"
#  cur.execute(query)
#  crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)
#  limitString=''
#  if args['limit']:
#    limitString=' limit '+args['limit']
#  if args['finyear']:
#    finyear=args['finyear']
# 
#  logger.info("DistrictName "+districtName)
##Query to get all the blocks
#  logger.info("crawlIP "+crawlIP)
#  logger.info("State Name "+stateName)
#  query="use %s" % districtName.lower()
#  cur.execute(query)
#  fullFinYear=getFullFinYear(finyear)
#
#
#  #ftofilepath=nregaDataDir.replace("stateName",stateName.title())+"/"+districtName.upper()+"/"
#  ftofilepath=nregaRawDataDir.replace("districtName",districtName.lower())
#  modifiedFTOFilePath=nregaWebDir.replace("stateName",stateName.upper()).replace("districtName",districtName.upper())
#   
##ftofilepath="/home/libtech/libtechdata/CHATTISGARH/"+districtName+"/"
# 
#  query=" select f.id,f.ftoNo,b.name from ftoDetails f,blocks b where b.blockCode=f.blockCode and b.isRequired=1 and f.isDownloaded=1 and f.isProcessed=0 and f.finyear='%s' %s" %(finyear,limitString)
#  cur.execute(query)
#  logger.info(query)
#  if cur.rowcount:
#    logger.info("The Number of FTOs Processed in is : "+str(cur.rowcount))
#    results = cur.fetchall()
#    for row in results:
#      isComplete=1
#      rowid=str(row[0])
#      ftoNo=row[1]
#      blockName=row[2]
#      logger.info(str(rowid)+"  "+finyear+"  "+ftoNo+"  "+blockName)
#      fullfinyear=getFullFinYear(finyear) 
#      ftofilename=ftofilepath+blockName.upper()+"/FTO/"+fullfinyear+"/"+ftoNo+".html"
#      modifiedFTOFileName=modifiedFTOFilePath+blockName.upper()+"/FTO/"+fullfinyear+"/"+ftoNo+".html"
#      logger.info(ftofilename)
#
#      if (os.path.isfile(ftofilename)): 
#        ftohtml=open(ftofilename,'r').read()
#      else:
#        ftohtml="Timeout expired"
#      if ("Timeout expired" in ftohtml) or ("Due to the heavy network traffic" in ftohtml) or ("The Values specified are wrong" in ftohtml) or ("The service is unavailable" in ftohtml):
#        errorflag=1
#      else:
#        errorflag,outhtml=alterFTOHTML(ftohtml)
#     
#      if errorflag==1:
#        logger.info("Invalid FTo HTML File please check") 
#        query="update ftoDetails set isDownloaded=0 where id=%s" % rowid 
#        logger.info(query)
#        cur.execute(query)
#      else:
#        logger.info("No Errors here, seems to be valid FTO File")
#        htmlHeaderLabels=["District Name","Block Name","FTO No"]
#        htmlHeaderValues=[districtName,blockName,ftoNo]
#        htmlHeader=genHTMLHeader(htmlHeaderLabels,htmlHeaderValues)
#
#        modifiedFTOHTML=htmlHeader+outhtml
#        modifiedFTOHTML=htmlWrapperLocal(title="FTO Details", head='<h1 aling="center">'+ftoNo+'</h1>', body=modifiedFTOHTML)
#        logger.info(modifiedFTOFileName)
#        writeFile(modifiedFTOFileName,modifiedFTOHTML)
# 
#        htmlsoup=BeautifulSoup(modifiedFTOHTML)
#        table=htmlsoup.find('table',id="ftoDetails")
#        rows = table.findAll('tr')
#        for tr in rows:
#          cols = tr.findAll('td')
#          tdtext=''
#          block= cols[1].string.strip()
#          logger.info("%s - %s " % (blockName,block.upper()))
#          if blockName.upper()==block.upper():
#            srno= cols[0].string.strip()
#            jobcardpanchayat="".join(cols[2].text.split())
#            referenceNo="".join(cols[3].text.split())
#            transactiondatestring="".join(cols[4].text.split())
#            applicantName=" ".join(cols[5].text.split())
#            wagelistNo="".join(cols[6].text.split())
#            primaryAccountHolder=" ".join(cols[7].text.split())
#            accountNo="".join(cols[8].text.split())
#            bankCode="".join(cols[9].text.split())
#            IFSCCode="".join(cols[10].text.split())
#            amounttobecredited="".join(cols[11].text.split())
#            creditedAmount="".join(cols[12].text.split())
#            status="".join(cols[13].text.split())
#            processeddatestring="".join(cols[14].text.split())
#            bankprocessdatestring="".join(cols[15].text.split())
#            utrNo="".join(cols[16].text.split())
#            rejectionReason=" ".join(cols[17].text.split())
#            panchayat=jobcardpanchayat[jobcardpanchayat.index("(") + 1:jobcardpanchayat.rindex(")")]
#            jobcard=jobcardpanchayat[0:jobcardpanchayat.index("(")]
#            logger.info(ftoNo+"  "+jobcard+"  "+panchayat)
#            transactionDate=NICToSQLDate(transactiondatestring)
#            processedDate=NICToSQLDate(processeddatestring)
#            bankProcessedDate=NICToSQLDate(bankprocessdatestring)
#            if processeddatestring == '':
#              isComplete=0
#
#            query="select * from ftoTransactionDetails where ftoNo='%s' and ftoIndex=%s" % (ftoNo,srno)
#            cur.execute(query)
#            if cur.rowcount == 0:
#              query="insert into ftoTransactionDetails (ftoNo,ftoIndex) values ('%s',%s) " % (ftoNo,srno)
#              logger.info(query)
#              cur.execute(query)
#            query="update ftoTransactionDetails set finyear='%s',referenceNo='%s',jobcard='%s',applicantName='%s',primaryAccountHolder='%s',accountNo='%s',wagelistNo='%s',transactionDate=%s,processedDate=%s,bankProcessedDate=%s,status='%s',rejectionReason='%s',utrNo='%s',creditedAmount=%s,bankCode='%s',IFSCCode='%s' where ftoNo='%s' and ftoIndex=%s " % (finyear,referenceNo,jobcard,applicantName,primaryAccountHolder,accountNo,wagelistNo,transactionDate,processedDate,bankProcessedDate,status,rejectionReason,utrNo,str(creditedAmount),bankCode,IFSCCode,ftoNo,srno)
#            logger.info(query)
#            cur.execute(query)
#        query="update ftoDetails set isProcessed=1,isComplete=%s where id=%s " % (str(isComplete),rowid)
#        logger.info(query)
#        cur.execute(query)    
#  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
#  logger.info("...END PROCESSING")     
#  exit(0)
#if __name__ == '__main__':
#  main()
