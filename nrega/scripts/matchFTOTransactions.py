from bs4 import BeautifulSoup
import MySQLdb
import os
import time
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
sys.path.insert(0, fileDir+'/../crawlDistricts/')
#sys.path.insert(0, rootdir)
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery,getjcNumber,getFullFinYear,writeFile
from crawlFunctions import getDistrictParams

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script to match FTO Table to Work Details Table')
  parser.add_argument('-d', '--district', help='Please enter the district', required=True)
  parser.add_argument('-af', '--additionalFilters', help='please enter additional filters', required=False)
  parser.add_argument('-f', '--finyear', help='Please enter the finyear', required=True)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit the number of entries that need to be processed', required=False)
  args = vars(parser.parse_args())
  return args

def getSmallSquareMatrix(logger,inMatrix):
  matchCountArray=[]
  for index,eachList in enumerate(inMatrix):
    logger.info("%s,%s" % (str(index),str(eachList)))
    count=0
    for a in inMatrix:
      if a == eachList:
        count=count+1
    matchCountArray.append(count)

  maxCount=max(matchCountArray)
  maxCountIndexArray=[]
  for index,count in enumerate(matchCountArray):
    if count==maxCount:
      maxCountIndexArray.append(index)
  
  if len(maxCountIndexArray) == 0:
    maxIndex=maxCountIndexArray[0]
  else:
    rowSum=0
    for eachIndex in maxCountIndexArray:
      curSum=sum(inMatrix[eachIndex])
      if curSum > rowSum:
        rowSum=curSum
        maxIndex=eachIndex

  logger.info(str(maxCount)+"-"+str(maxIndex))
  maxRow=inMatrix[maxIndex]
  maxValueinRow=max(maxRow)
  maxValueinRowCount=maxRow.count(maxValueinRow)
  hasSmallSquareMatrix=0
  if maxValueinRowCount == maxCount:
    logger.info("This would give us a perfect square Matrix Matrix to Match")
    hasSmallSquareMatrix=1
  validRowArray=[]
  validColumnArray=[]
  for index,r in enumerate(inMatrix):
    if r==maxRow:
      validRowArray.append(index)
  for index,c in enumerate(maxRow):
    if c==maxValueinRow:
      validColumnArray.append(index)

  logger.info("Valid Columns : %s, Valid Rows %s " % (str(validColumnArray),str(validRowArray)))
  return hasSmallSquareMatrix,validRowArray,validColumnArray

def isSingleValueMatrix(logger,inMatrix):
  totalElements=len(inMatrix) * len(inMatrix[0])
  firstValue=inMatrix[0][0]
  totalFirstValueElements=sum(x.count(firstValue) for x in inMatrix)
  logger.info("Total Elements in Matrix : %s Same Values : %s " % (str(totalElements),str(totalFirstValueElements)))
  if totalElements == totalFirstValueElements:
    singleValueMatrix=1
  else:
    singleValueMatrix=0
  return singleValueMatrix

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("BEGIN PROCESSING...")
  
  if args['limit']:
    limitString=" limit %s " % (str(args['limit']))
  else:
    limitString="  "
  districtName=args['district'].lower()
  finyear=args['finyear'].lower()
  fullfinyear=getFullFinYear(finyear)
  additionalFilter=''
  if args['additionalFilters']:
    additionalFilter=" and "+args['additionalFilters']
   
  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)


  whereClause="and wdRecordAbsent=0 and perfectMatch=0 and matchComplete=0 " 

  query="select count(*),jobcard,wagelistNo,ftoNo,creditedAmount from ftoTransactionDetails where finyear='%s' %s %s group by jobcard,wagelistNo,ftoNo,creditedAmount order by wagelistNo,jobcard,creditedAmount DESC %s" % (finyear,additionalFilter,whereClause,limitString)
  logger.info(query)
  cur.execute(query)
  results=cur.fetchall()
  for row1 in results:
    count = row1[0]
    jobcard = row1[1]
    wagelistNo = row1[2]
    ftoNo =row1[3]
    if row1[4] is None:
      ftoCreditedAmountClause="creditedAmount is NULL"
    else:
      ftoCreditedAmountClause="creditedAmount=%s " % row1[4]
    

    query="select * from workDetails where jobcard='%s' and wagelistNo='%s' and matchComplete=0" % (jobcard,wagelistNo)
    cur.execute(query)
    wdCount = cur.rowcount
    logger.info("WagelistNo: %s   ftoNo: %s  jobcard: %s    count: %s  wdCount=%s" % (wagelistNo,ftoNo,jobcard,str(count),str(wdCount)))

    #Now First we need to see if we have any entries in Work Details table matching the wagelist and Jobcard, if the count is zero then we need to update ftoTransactionDetails Table with wdRecordAbsent
    if wdCount == 0:
      query="update ftoTransactionDetails set wdRecordAbsent=1  where jobcard='%s' and wagelistNo='%s' and ftoNo='%s' and %s %s" % (jobcard,wagelistNo,ftoNo,ftoCreditedAmountClause,whereClause)
      cur.execute(query)

    #Need to create a Matrix in case the Work Details count does not equal to zero    
    if wdCount > 0:
      matchMatrix=[]  # This is a Two Dimensional Array
      wdIDMatrix=[]
      matchStringMatrix=[]
      maxIndexArray=[]
      query="select id,applicantName,accountNo,status,creditedAmount from ftoTransactionDetails where jobcard='%s' and wagelistNo='%s' and ftoNo='%s' and %s %s" % (jobcard,wagelistNo,ftoNo,ftoCreditedAmountClause,whereClause)
      logger.info(query)
      cur.execute(query)
      ftoResults=cur.fetchall()
      i=0
      ftIDArray=[]
      ftValidMatchArray=[]
      for ftoRow in ftoResults:
        ftID= ftoRow[0]
        ftoName=ftoRow[1]
        ftoAccountNo=ftoRow[2]
        ftoStatus=ftoRow[3]
        ftoAmount=ftoRow[4]
        ftIDArray.append(ftID)
        ftValidMatchArray.append(0)
        matchMatrix.append([]) 
        matchStringMatrix.append([])
        wdIDMatrix.append([])
        query="select id,name,accountNo,totalWage,musterStatus from workDetails where jobcard='%s' and wagelistNo='%s' and matchComplete=0" % (jobcard,wagelistNo)
        logger.info(query)
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
        if maxCount == 1 and maxMatch>0:
          maxIndex=matchMatrix[i].index(maxMatch)
        else:
          maxIndex=None
        maxIndexArray.append(maxIndex) 
        i=i+1

      logger.info("MatchMatrix : %s " % str(matchMatrix))
      logger.info("matchStringMatrix : %s " % str(matchStringMatrix))
      logger.info("maxIndex Array : %s " % str(maxIndexArray))
      maxIndexArrayWithoutNone=[x for x in maxIndexArray if x != None]
      singleValueMatrix=isSingleValueMatrix(logger,matchMatrix)
      logger.info("Single Value Matrix : %s " % (singleValueMatrix))
      hasSmallSquareMatrix,validRowArray,validColumnArray=getSmallSquareMatrix(logger,matchMatrix) 
      doMatch=0
     # if (len(maxIndexArray) == len(set(maxIndexArray))) and (None not in maxIndexArray):
      if ((len(maxIndexArrayWithoutNone) == len(set(maxIndexArrayWithoutNone))) and (len(maxIndexArrayWithoutNone) != 0)):
        for myindex,myvalue in enumerate(ftValidMatchArray):
          if maxIndexArray[myindex] is not None:
            ftValidMatchArray[myindex] = 1
        doMatch=1
      elif (len(maxIndexArray) != len(set(maxIndexArray))) and (None not in maxIndexArray):
        if (count > wdCount) and (wdCount == 1): #If FTO Entries are greater than WorkDetails Entries
          i=0
          maxValue=0
          maxIndex=None
          while i < count:
            if matchMatrix[i][0] > maxValue:
              maxValue=matchMatrix[i][0]
              maxIndex=i
            i=i+1
          logger.info("Max Index is %s" % (str(maxIndex)))
          ftValidMatchArray[maxIndex]=1
          doMatch=1
      elif ( (count == wdCount) and (singleValueMatrix == 1)):
        logger.info("It seems all values of Matrix are same")
        ftoIndex=0
        while ftoIndex < count:
          maxIndexArray[ftoIndex] = ftoIndex
          ftValidMatchArray[ftoIndex] = 1
          ftoIndex=ftoIndex+1
        doMatch=1 
      elif (hasSmallSquareMatrix == 1):
        for index,r in enumerate(validRowArray):
          ftValidMatchArray[r] = 1
          maxIndexArray[r] = validColumnArray[index]
        doMatch=1

  
      logger.info("FT Valid Match Array %s " % str(ftValidMatchArray)) 
      if doMatch == 1:
        ftoIndex=0
        for maxIndex in maxIndexArray:
          if ftValidMatchArray[ftoIndex] == 1:
            curFTID=ftIDArray[ftoIndex]
            curWDID=wdIDMatrix[ftoIndex][maxIndex]
            curMatchString=matchStringMatrix[ftoIndex][maxIndex]
            logger.info("Matching FTOID : %s  WorkDetails ID : %s curMatchString = %s " % (str(curFTID),str(curWDID),curMatchString))
            query="update ftoTransactionDetails set matchComplete=1,workDetailsID=%s,matchType='%s' where id=%s " %(str(curWDID),curMatchString,str(curFTID))
            logger.info(query)
            cur.execute(query)
            query="update workDetails set matchComplete=1 where id='%s' " % (str(curWDID))
            logger.info(query)
            cur.execute(query)
          ftoIndex=ftoIndex+1
           
      #Reference Queries
      query="select id,applicantName,accountNo,creditedAmount,status from ftoTransactionDetails where jobcard='%s' and wagelistNo='%s' and ftoNo='%s' and %s" % (jobcard,wagelistNo,ftoNo,ftoCreditedAmountClause)
      logger.info(query) 
      query="select id,name,accountNo,totalWage,musterStatus from workDetails where jobcard='%s' and wagelistNo='%s' " % (jobcard,wagelistNo)
      logger.info(query) 
        
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
