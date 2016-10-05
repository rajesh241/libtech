from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
import time
import re
import sys
from MySQLdb import OperationalError
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../includes/')
sys.path.insert(0, fileDir+'/../')
#sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery
from globalSettings import datadir,nregaDataDir
from biharSettings import pdsDataDir
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Populate Pds SHop codes from csv File')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-id', '--rowid', help='Process Particular rowID', required=False)
  parser.add_argument('-limit', '--limit', help='Limit the number of Runs', required=False)

  args = vars(parser.parse_args())
  return args
def extractDetailInfo(logger,detailInfo):
  dummyString=",,"
  a=re.search('Driver Name :(.*)',detailInfo)
  isComplete=1
  if a:
    b=a.group(1)
    logger.info("Drive Name %s " % b)
    driverArray=b.split(",")
  else:
    logger.info("Driver Information Does not exists")
    driverArray=dummyString.split(",")
    isComplete=0
  a=re.search('Vehicle No. :(.*)',detailInfo)
  if a:
    b=a.group(1)
    logger.info("Vehicle No %s " % b)
    vehicleArray=b.split(",")
  else:
    logger.info("Vehicle Information Does not exists")
    vehicleArray=dummyString.split(",")
    isComplete=0
  a=re.search('Date of Delivered. :(.*)',detailInfo)
  if a:
    b=a.group(1)
    logger.info("Dates %s " % b)
    dateArray=b.split(",")
  else:
    logger.info("Date Information Does not exists")
    dateArray=dummyString.split(",")
    isComplete=0
  return isComplete,driverArray,vehicleArray,dateArray

def main():
  monthLabels=['0','JAN','FEB','MAR','APR','MAY','JUNE','JULY','AUG','SEP','OCT','NOV','DEC']
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  db = dbInitialize(db="biharPDS", charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  limitString=""
  if args['limit']:
    limitString="limit %s " % args['limit']
  filterClause=''
  if args['rowid']:
    rowid=args['rowid'].lower()
    filterClause=' and pd.id=%s ' % rowid
  rowid='19632';
  
  query="select pd.id,pd.distCode,pd.blockCode,pd.fpsCode,pd.fpsMonth,pd.fpsYear,ps.distName,ps.blockName,ps.fpsName from pdsShopsDownloadStatus pd,pdsShops ps where pd.distCode=ps.distCode and pd.blockCode=ps.blockCode and pd.fpsCode=ps.fpsCode and pd.isDownloaded=1 and (pd.statusRemark != 'completeRecord' or pd.statusRemark is NULL) %s %s" % (filterClause,limitString)
  logger.info(query)
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    statusRemark=''
    rowid=row[0]
    logger.info("Row ID %s " %str(rowid))
    distCode=row[1]
    blockCode=row[2]
    fpsCode=row[3]
    fpsMonth=row[4]
    fpsYear=row[5]
    distName=row[6]
    blockName=row[7]
    fpsName=row[8]
    myfilename="%s/%s/%s/%s/%s/%s.html" % (pdsDataDir,str(fpsYear),monthLabels[int(fpsMonth)],distName.upper(),blockName.upper(),fpsCode+"_"+fpsName)
    myfilename=myfilename.replace(" ","_")
    logger.info(myfilename)
    f1=open(myfilename,'r')
    fpsHtml=f1.read()
    fpsSoup=BeautifulSoup(fpsHtml,"lxml")
    tables=fpsSoup.findAll('table',{"class" : "newFormTheme"})
    i=0
    dealerTablePresent=0
    deliveryTablePresent=0
    for table in tables:
      #print table1
      i=i+1
     # if i == 1:
      if "Dealer Name" in str(table):
         # logger.info("This does not have a Dealer Information Table")
         # statusRemark='noDealerInformation'
        dealerTablePresent = 1
        table1Rows=table.findAll('tr')
        for eachRow in table1Rows:
          #print eachRow
          table1Cols=eachRow.findAll('td')
          #print len(table1Cols)
          if len(table1Cols) == 3:
            locality=table1Cols[2].text.lstrip().rstrip()
            logger.info("Locality : %s " % locality)
            #print locality
      elif "SIO Status" in str(table):
        deliveryTablePresent=1
        table2Rows=table.findAll('tr')
        for eachRow in table2Rows:
          #print eachRow
          table2Cols=eachRow.findAll('td')
          table2thCols=eachRow.findAll('th')
          #print table2Cols
          #print len(table2Cols)
          if len(table2Cols)==8:
            dateofdelivery=table2Cols[7].text
            detailInfo=table2Cols[7].text
            #logger.info("Detailed Information %s" % detailInfo)
            isComplete,driverArray,vehicleArray,dateArray=extractDetailInfo(logger,detailInfo)
            scheme=table2thCols[0].text.lstrip().rstrip()
            allot_wheat=table2Cols[0].text.lstrip().rstrip().replace(",","")
            allot_rice=table2Cols[1].text.lstrip().rstrip().replace(",","")
            amountWheat=table2Cols[3].text.lstrip().rstrip().replace(",","")
            amountRice=table2Cols[4].text.lstrip().rstrip().replace(",","")
            status=table2Cols[2].text.lstrip().rstrip()
            sioStatus=table2Cols[6].text.lstrip().rstrip()
            dateFormat='%d-%m-%Y'
            if isComplete==0:
              statusRemark="deliveryDateAbsent"
            else:
              statusRemark="completeRecord"
            #amount_wheat=table2Cols[4].text.lstrip().rstrip()
            #amount_rice=table2Cols[5].text.lstrip().rstrip()
            logger.info("scheme: %s   wheat : %s rice : %s  status : %s sioStatus: %s" % (scheme,allot_wheat,allot_rice,status,sioStatus))
            query="select id from pdsShopsMonthlyStatus where scheme='%s' and distCode='%s' and blockCode='%s' and fpsCode='%s' and fpsYear='%s' and fpsMonth='%s'" %(scheme,distCode,blockCode,fpsCode,fpsYear,fpsMonth)
            cur.execute(query)
            if cur.rowcount == 0:
              query="insert into pdsShopsMonthlyStatus (scheme,distCode,blockCode,fpsCode,fpsYear,fpsMonth) values ('%s','%s','%s','%s','%s','%s')" % (scheme,distCode,blockCode,fpsCode,fpsYear,fpsMonth)
              cur.execute(query)
              detailsID=str(cur.lastrowid)
            else:
              row1=cur.fetchone() 
              detailsID=str(row1[0])
               
            logger.info(query)
            query="update pdsShopsMonthlyStatus set scheme='%s',allotWheat=%s,allotRice=%s,amountWheat=%s,amountRice=%s,status='%s',sioStatus='%s',driverName0='%s',vehicle0='%s',dateOfDelivery0=STR_TO_DATE('%s','%s'),driverName1='%s',vehicle1='%s',dateOfDelivery1=STR_TO_DATE('%s','%s') where id=%s" %(scheme,allot_wheat,allot_rice,amountWheat,amountRice,status,sioStatus,driverArray[0],vehicleArray[0],dateArray[0].lstrip()[:10],dateFormat,driverArray[1],vehicleArray[1],dateArray[1].lstrip()[:10],dateFormat,str(detailsID))
            logger.info(query)
            cur.execute(query)
          else:
            statusRemark="noDeliveryInformation"

    if deliveryTablePresent == 1:
      finalStatusRemark = statusRemark
    else:
      if dealerTablePresent == 0:
        finalStatusRemark = "dealerTableMissing"
      else:
        finalStatusRemark = "deliveryTableMissing"
    f1.close()
    logger.info("Status of File = %s " %(finalStatusRemark))
    query="update pdsShopsDownloadStatus set statusRemark='%s' where id=%s " % (finalStatusRemark,str(rowid))
    logger.info(query)
    cur.execute(query)
    if finalStatusRemark != 'completeRecord':
      query="update pdsShopsDownloadStatus set isDownloaded=0 where id=%s " %(str(rowid))
      logger.info(query)
      cur.execute(query)
 




  dbFinalize(db) # Make sure you put this if there are other exit paths or errors


  
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()
