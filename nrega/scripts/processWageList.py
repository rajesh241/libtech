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

  parser = argparse.ArgumentParser(description='Script to Process Wagelist')
  parser.add_argument('-d', '--district', help='Please enter the district', required=True)
  parser.add_argument('-af', '--additionalFilters', help='please enter additional filters', required=False)
  parser.add_argument('-f', '--finyear', help='Please enter the finyear', required=True)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit the number of entries that need to be processed', required=False)
  args = vars(parser.parse_args())
  return args
  
 
def main():
  regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
  regex1=re.compile(r'</td></font></td>',re.DOTALL)
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  
  if args['district']:
    districtName=args['district'].lower()
  if args['finyear']:
    finyear=args['finyear'].lower()
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
  filepath=nregaRawDataDir.replace("districtName",districtName.lower())
  modifiedFilepath=nregaWebDir.replace("stateName",stateName.upper()).replace("districtName",districtName.upper())
  fullfinyear=getFullFinYear(finyear)
  ftoPrefix=stateShortCode+stateCode+districtCode
  logger.info(ftoPrefix)
  query="select w.id,w.wagelistNo,w.blockCode,b.name from wagelists w, blocks b where  b.blockCode=w.blockCode and w.isDownloaded=1 and w.isProcessed=0 and w.finyear='%s' %s" % (finyear,limitString)
  logger.info(query)
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    wagelistError=0
    isComplete=1
    rowid=str(row[0])
    wagelistNo=row[1]
    blockCode=row[2]
    blockName=row[3]
    filename=filepath+blockName.upper()+"/WAGELIST/"+fullfinyear+"/"+wagelistNo+".html"
    modifiedFilename=modifiedFilepath+blockName.upper()+"/WAGELIST/"+fullfinyear+"/"+wagelistNo+".html"
    logger.info(filename)
    myhtml=open(filename,'r').read()
    #To Rewrite wagelist HTML
    htmlHeaderLabels=["District Name","Block Name","Wagelist No"]
    htmlHeaderValues=[districtName,blockName,wagelistNo]
    htmlHeader=genHTMLHeader(htmlHeaderLabels,htmlHeaderValues)
    outhtml=alterHTMLTables(myhtml)
    modifiedHTML=htmlHeader+outhtml
    modifiedHTML=htmlWrapperLocal(title="Wagelist Details", head='<h1 aling="center">'+wagelistNo+'</h1>', body=modifiedHTML)
    logger.info("Modified File Name %s " % modifiedFilename)
    writeFile(modifiedFilename,modifiedHTML)

    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    tables=htmlsoup.findAll('table')
    for table in tables:
      if "WageList Agency Code" in str(table):
        rows=table.findAll('tr')
        for row in rows:
          cols=row.findAll('td')
          jobcard=cols[8].text.strip().lstrip().rstrip()
          if jobcard != "Reg No.":
            ftoNo=cols[12].text.strip().lstrip().rstrip()
            if ftoPrefix in ftoNo:
              query="select * from ftoDetails where ftoNo='%s' and blockCode='%s' and finyear='%s'" % (ftoNo,blockCode,finyear)
              cur.execute(query)
              if cur.rowcount==0:
                logger.info("FTo Record does not exists")
                query="insert into ftoDetails (ftoNo,blockCode,finyear) values ('%s','%s','%s')" % (ftoNo,blockCode,finyear)
                cur.execute(query)
            else:
              isComplete=0
    query="update wagelists set processedDate=NOW(),isProcessed=1,isError=%s,isComplete=%s where id=%s" % (str(wagelistError),str(isComplete),str(rowid))
    cur.execute(query)
          
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
