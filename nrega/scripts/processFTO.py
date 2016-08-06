
import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import time
import re
import os
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
from globalSettings import datadir
#Error File Defination
errorfile = open('/tmp/processFTO.log', 'a')
sys.path.insert(0, fileDir+'/../../')
from globalSettings import nregaDir 
from libtechFunctions import getFullFinYear,singleRowQuery
#Connect to MySQL Database
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from crawlFunctions import getDistrictParams
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for Downloading FTOs')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit the number of ftos to be downloaded', required=False)
  parser.add_argument('-d', '--district', help='District for which you need to Download', required=True)
  parser.add_argument('-f', '--finyear', help='Input Financial Year', required=True)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  if args['district']:
    districtName=args['district']

  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)
  limitString=''
  if args['limit']:
    limitString=' limit '+args['limit']
  if args['finyear']:
    infinyear=args['finyear']
 
  logger.info("DistrictName "+districtName)
#Query to get all the blocks
  logger.info("crawlIP "+crawlIP)
  logger.info("State Name "+stateName)
  query="use %s" % districtName.lower()
  cur.execute(query)



  #ftofilepath=nregaDataDir.replace("stateName",stateName.title())+"/"+districtName.upper()+"/"
  htmlDir=nregaDir.replace("districtName",districtName.lower())
  ftofilepath=htmlDir+"/"+districtName.upper()+"/"
#ftofilepath="/home/libtech/libtechdata/CHATTISGARH/"+districtName+"/"
 
  query=" select f.id,f.ftoNo,b.name,f.finyear from ftoDetails f,blocks b where b.blockCode=f.blockCode and b.isRequired=1 and f.isDownloaded=1 and f.isProcessed=0 and f.finyear='%s' %s" %(infinyear,limitString)
  cur.execute(query)
  logger.info(query)
  if cur.rowcount:
    logger.info("The Number of FTOs Processed in is : "+str(cur.rowcount))
    results = cur.fetchall()
    for row in results:
      ftoid=row[0]
      ftoNo=row[1]
      blockName=row[2]
      finyear=row[3]
      logger.info(str(ftoid)+"  "+finyear+"  "+ftoNo+"  "+blockName)
      fullfinyear=getFullFinYear(finyear) 
      ftofilename=ftofilepath+blockName.upper()+"/FTO/"+fullfinyear+"/"+ftoNo+".html"
      logger.info(ftofilename)
      if (os.path.isfile(ftofilename)): 
        ftohtml=open(ftofilename,'r').read()
      else:
        ftohtml="Timeout expired"
      if ("Timeout expired" in ftohtml) or ("The Values specified are wrong" in ftohtml):
        logger.info("This is time out expired file")
        errorflag=1
        query="update ftoDetails set isDownloaded=0 where id="+str(ftoid)
        cur.execute(query)
      else:
        htmlsoup=BeautifulSoup(ftohtml)
        try:
          table=htmlsoup.find('table',id="ftoDetails")
          rows = table.findAll('tr')
          errorflag=0
        except:
          errorflag=1
          query="update ftoDetails set isDownloaded=0 where id="+str(ftoid)
          cur.execute(query)
   
      if errorflag==0:
        for tr in rows:
          cols = tr.findAll('td')
          tdtext=''
          logger.info("Error flag is Zero")
          block= cols[1].string.strip()
          logger.info("%s - %s " % (blockName,block.upper()))
          if blockName.upper()==block.upper():
            srno= cols[0].string.strip()
            jobcardpanchayat="".join(cols[2].text.split())
            referenceNo="".join(cols[3].text.split())
            transactiondatestring="".join(cols[4].text.split())
            applicantName=" ".join(cols[5].text.split())
            wagelistNo="".join(cols[6].text.split())
            primaryAccountHolder=" ".join(cols[7].text.split())
            accountNo="".join(cols[8].text.split())
            bankCode="".join(cols[9].text.split())
            IFSCCode="".join(cols[10].text.split())
            amounttobecredited="".join(cols[11].text.split())
            creditedAmount="".join(cols[12].text.split())
            status="".join(cols[13].text.split())
            processeddatestring="".join(cols[14].text.split())
            bankprocessdatestring="".join(cols[15].text.split())
            utrNo="".join(cols[16].text.split())
            rejectionReason=" ".join(cols[17].text.split())
            panchayat=jobcardpanchayat[jobcardpanchayat.index("(") + 1:jobcardpanchayat.rindex(")")]
            jobcard=jobcardpanchayat[0:jobcardpanchayat.index("(")]
            #print panchayat+"  "+jobcard
            if transactiondatestring != '':
              transactiondate = time.strptime(transactiondatestring, '%d/%m/%Y')
              transactiondate = time.strftime('%Y-%m-%d %H:%M:%S', transactiondate)
            else:
              transactiondate=''
            if processeddatestring != '':
              processeddate = time.strptime(processeddatestring, '%d/%m/%Y')
              processeddate = time.strftime('%Y-%m-%d %H:%M:%S', processeddate)
              processeddate="'%s'" % processeddate
            else:
        			processeddate='NULL'
            if bankprocessdatestring != '':
              bankprocessdate = time.strptime(bankprocessdatestring, '%d/%m/%Y')
              bankprocessdate = time.strftime('%Y-%m-%d %H:%M:%S', bankprocessdate)
            else:
              bankprocessdate=''
            logger.info(ftoNo+"  "+jobcard+"  "+panchayat)
            query="insert into ftoTransactionDetails (finyear,ftoNo,referenceNo,jobcard,applicantName,primaryAccountHolder,accountNo,wagelistNo,transactionDate,processedDate,status,rejectionReason,utrNo,creditedAmount,bankCode,IFSCCode) values ('"+finyear+"','"+ftoNo+"','"+referenceNo+"','"+jobcard+"','"+applicantName+"','"+primaryAccountHolder+"','"+accountNo+"','"+wagelistNo+"','"+transactiondate+"',"+processeddate+",'"+status+"','"+rejectionReason+"','"+utrNo+"',"+str(creditedAmount)+",'"+bankCode+"','"+IFSCCode+"');"
            logger.info(query)
            try:
              cur.execute(query)
            except MySQLdb.IntegrityError,e:
              errormessage=(time.strftime("%d/%m/%Y %H:%M:%S "))+str(e)+"\n"
              errorfile.write(errormessage)
              continue
        query="update ftoDetails set isProcessed=1 where id="+str(ftoid);
      #print query
        cur.execute(query)

  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
