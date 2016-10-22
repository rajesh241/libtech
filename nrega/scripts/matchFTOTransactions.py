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

  fullfinyear=getFullFinYear(finyear)
  
  query="select count(*),jobcard,wagelistNo,ftoNo from ftoTransactionDetails where finyear='%s' and matchType is NULL group by jobcard,wagelistNo,ftoNo %s " % (finyear,limitString)
  query="select count(*),jobcard,wagelistNo,ftoNo from ftoTransactionDetails where finyear='%s' %s and wdRecordAbsent=0 and perfectMatch=0 and matchComplete=0 group by jobcard,wagelistNo,ftoNo %s " % (finyear,additionalFilter,limitString)
  logger.info(query)
  cur.execute(query)
  results=cur.fetchall()
  for row1 in results:
    count = row1[0]
    jobcard = row1[1]
    wagelistNo = row1[2]
    ftoNo =row1[3]

    query="select * from workDetails where jobcard='%s' and wagelistNo='%s'" % (jobcard,wagelistNo)
    cur.execute(query)
    wdCount = cur.rowcount
    
    logger.info("WagelistNo: %s   ftoNo: %s  jobcard: %s    count: %s  wdCount=%s" % (wagelistNo,ftoNo,jobcard,str(count),str(wdCount)))


    if wdCount == 0:
      query="update ftoTransactionDetails set wdRecordAbsent=1  where jobcard='%s' and wagelistNo='%s' and ftoNo='%s' " % (jobcard,wagelistNo,ftoNo)
      cur.execute(query)

    if count >0 and wdCount > 0:#== wdCount:
      logger.info("The counts are Matching, so we can make perfect co relation")
      matchMatrix=[]  # This is a Two Dimensional Array
      wdIDMatrix=[]
      matchStringMatrix=[]
      maxIndexArray=[]
      query="select id,applicantName,accountNo,status,creditedAmount from ftoTransactionDetails where jobcard='%s' and wagelistNo='%s' and ftoNo='%s' " % (jobcard,wagelistNo,ftoNo)
      cur.execute(query)
      ftoResults=cur.fetchall()
      i=0
      ftIDArray=[]
      equalMatch=0
      for ftoRow in ftoResults:
        ftID= ftoRow[0]
        ftoName=ftoRow[1]
        ftoAccountNo=ftoRow[2]
        ftoStatus=ftoRow[3]
        ftoAmount=ftoRow[4]
        ftIDArray.append(ftID)
        matchMatrix.append([]) 
        matchStringMatrix.append([])
        wdIDMatrix.append([])
        query="select id,name,accountNo,totalWage,musterStatus from workDetails where jobcard='%s' and wagelistNo='%s'" % (jobcard,wagelistNo)
        cur.execute(query)
        musterResults=cur.fetchall()
        for musterRow in musterResults:
          wdID=musterRow[0]
          musterName=musterRow[1]
          musterAccountNo=musterRow[2]
          musterAmount=musterRow[3]
          musterStatus=musterRow[4]
          matchCount=0
          matchString=''
          if ftoName.replace(" ","").lower() in musterName.replace(" ","").lower():
            matchCount = matchCount +1
            matchString+="nameMatch"
          else:
            matchString+="nameMismatch"
          if ftoAccountNo == musterAccountNo:
            matchCount = matchCount +1
            matchString+="AccountMatch"
          else:
            matchString+="AccountMismatch"
          if (ftoAmount is not None) and (int(ftoAmount)==int(musterAmount)):
            matchCount = matchCount + 1
          if musterStatus == 'Credited':
             musterStatus="Processed"
          if ( (musterStatus==ftoStatus.replace(" ",""))  and (musterStatus != '') ):
            matchCount = matchCount + 1
          matchMatrix[i].append(matchCount)
          matchStringMatrix[i].append(matchString)
          wdIDMatrix[i].append(wdID)

        maxMatch=max(matchMatrix[i])
        maxCount=matchMatrix[i].count(maxMatch)
        
        if maxCount == 1:
          maxIndex=matchMatrix[i].index(maxMatch)
        else:
          maxIndex=None
          equalMatch=1
        maxIndexArray.append(maxIndex) 
        i=i+1
        
      i=0
      logger.info("MatchMatrix : %s " % str(matchMatrix))
      logger.info("maxIndex Array : %s " % str(maxIndexArray))

# Now we shall do the Mappint

      if len(maxIndexArray) == len(set(maxIndexArray)):
         logger.info("Perfect Matching")
         query="update ftoTransactionDetails set perfectMatch=1  where jobcard='%s' and wagelistNo='%s' and ftoNo='%s' " % (jobcard,wagelistNo,ftoNo)
         cur.execute(query) 
         
         #If for some case equal match is there, we need to match it to pending one.
         if (equalMatch == 1) and (count==wdCount):
           pendingArray=[]
           equalMatchIndex=maxIndexArray.index(None)
           i=0
           while i < wdCount:
             if i not in maxIndexArray:
               pendingArray.append(i)
             i=i+1
           if len(pendingArray) == 1:
             maxIndexArray[equalMatchIndex]=pendingArray[0]
             equalMatch=0
           logger.info("Number of Equal Matches: %s Pending Array : %s " % ( str(equalMatchIndex),str(pendingArray)))
         #Lets do the ftoID and musterID Matching
         ftoIndex=0
         if equalMatch==0:
           for maxIndex in maxIndexArray:
             curFTID=ftIDArray[ftoIndex]
             curWDID=wdIDMatrix[ftoIndex][maxIndex]
             curMatchString=matchStringMatrix[ftoIndex][maxIndex]
             ftoIndex=ftoIndex+1
             logger.info("Matching FTOID : %s  WorkDetails ID : %s curMatchString = %s " % (str(curFTID),str(curWDID),curMatchString))
             query="update ftoTransactionDetails set matchComplete=1,workDetailsID=%s,matchType='%s' where id=%s " %(str(curWDID),curMatchString,str(curFTID))
             logger.info(query)
             cur.execute(query)
           
      else:
         logger.info("Not a Great Match")
         # Here we wold need to write the logic when the number of Nones is greater than 1
         if (equalMatch == 1) and (count == wdCount):
           pendingArray=[]
           i=0
           while i < wdCount:
             if i not in maxIndexArray:
               pendingArray.append(i)
             i=i+1
           logger.info("Pending array: %s " % (str(pendingArray)))
           
         if count > wdCount:
           logger.info("Few workDetails available") 
           if wdCount == 1:
             i=0
             maxValue=0
             maxIndex=None
             while i < count:
               if matchMatrix[i][0] > maxValue:
                 maxValue=matchMatrix[i][0]
                 maxIndex=i
               i=i+1
                   
             if maxIndex is not None:
               curFTID=ftIDArray[maxIndex]
               curWDID=wdIDMatrix[maxIndex][0]  
               curMatchString=matchStringMatrix[maxIndex][0]  
               logger.info("Matching FTOID : %s  WorkDetails ID : %s curMatchString = %s " % (str(curFTID),str(curWDID),curMatchString))
               query="update ftoTransactionDetails set matchComplete=1,workDetailsID=%s,matchType='%s' where id=%s " %(str(curWDID),curMatchString,str(curFTID))
               logger.info(query)
               cur.execute(query)
             #For other elements in this list we need to make them matchNotFound
             i=0
             while i < count:
               if i != maxIndex:
                 curFTID=ftIDArray[i]
                 query="update ftoTransactionDetails set wdRecordAbsent=1 where id=%s " % (str(curFTID))
                 logger.info(query)
                 cur.execute(query)
               i = i+1

    else:
      b=1
     # logger.info("The counts are not Matching Yet so we will still need to figure out")
    #Example Query
    query="select id,applicantName,accountNo,creditedAmount,status from ftoTransactionDetails where jobcard='%s' and wagelistNo='%s' " % (jobcard,wagelistNo)
    logger.info(query) 
    query="select id,name,accountNo,totalWage,musterStatus from workDetails where jobcard='%s' and wagelistNo='%s' " % (jobcard,wagelistNo)
    logger.info(query) 
                
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()


