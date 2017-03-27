from bs4 import BeautifulSoup
import multiprocessing, time
import requests
import MySQLdb
import os
import os.path
import time
import re
import sys
from MySQLdb import OperationalError
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
#sys.path.insert(0, rootdir)
import datetime
from wrappers.logger import loggerFetch
from wrappers.db import dbInitialize,dbFinalize
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from crawlSettings import nregaDB 
from crawlSettings import nregaWebDir,nregaRawDataDir,tempDir
from crawlFunctions import alterHTMLTables,writeFile,getjcNumber,NICToSQLDate,getFullFinYear,htmlWrapperLocal
def rewriteRejectedTable(inhtml,tableID):
  tableHTML=''
  classAtt='id = "%s" border=1 class = " table table-striped"' % tableID
  tableHTML+='<table %s>' % classAtt
  rows=inhtml.findAll('tr')
  for eachRow in rows:
    if "Green" in str(eachRow):
       className="success"
    elif "Yellow" in str(eachRow):
       className="warning"
    elif "Blue" in str(eachRow):
       className="blue"
    else:
       className="danger"
    thCols=eachRow.findAll('th')
    if len(thCols) > 1:
     tableHTML+='<tr class="info">'
     for eachTD in thCols:
       tableHTML+='<th>%s</th>' % eachTD.text
     tableHTML+='</tr>'

    tdCols=eachRow.findAll('td')
    if len(tdCols) > 1:
      tableHTML+='<tr class="%s">' %(className)
      for eachTD in tdCols:
        tableHTML+='<td>%s</td>' % eachTD.text
      tableHTML+='</tr>'

  tableHTML+='</table>'
  return tableHTML


def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing Jobcards')
  parser.add_argument('-dc', '--districtCode', help='District for which you need to Download', required=False)
  parser.add_argument('-s', '--state', help='State Name', required=False)
  parser.add_argument('-f', '--finyear', help='Download musters for that finyear', required=True)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-d', '--download', help='Download Rejected Payments', required=False,action='store_const', const=1)
  parser.add_argument('-p', '--process', help='Process Rejected Payments', required=False,action='store_const', const=1)
  parser.add_argument('-limit', '--limit', help='District for which you need to Download', required=False)

  args = vars(parser.parse_args())
  return args
def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("BEGIN PROCESSING...")
  finyear=args['finyear']
  fullfinyear=getFullFinYear(finyear)
  limitString=''
  if args['limit']:
    limitString=" limit %s " % args['limit']
  additionalFilters=''
  if args['districtCode']:
    additionalFilters+= " and d.fullDistrictCode='%s' " % args['districtCode']
  if args['state']:
    additionalFilters+= " and d.stateName='%s' " % args['state']
  db = dbInitialize(db=nregaDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  if args['download']: 
    query="select d.fullDistrictCode,d.crawlIP,d.stateCode,d.stateName,d.rawDistrictName,d.districtName from districts d,districtStatus ds where d.fullDistrictCode=ds.fullDistrictCode  %s order by ds.rejectedPaymentCrawlAttemptDate %s " % (additionalFilters,limitString)
    logger.info(query)
    cur.execute(query)
    results=cur.fetchall()
    for row in results:
      [fullDistrictCode,crawlIP,stateCode,stateName,rawDistrictName,districtName] = row
      url="http://%s/netnrega/FTO/rejection.aspx?lflag=local&page=s&state_code=%s&fin_year=%s&state_name=%s&district_code=%s&district_name=%s&typ=R&linkr=X&" % (crawlIP,stateCode,fullfinyear,stateName,fullDistrictCode,rawDistrictName)
      filepath=nregaWebDir.replace("stateName",stateName.upper()).replace("districtName",districtName.upper())
      filenameRaw=filepath+"/misc/%s_rejectedPayments_%s_orig.html" % (districtName.upper(),fullfinyear)
      filename=filepath+"/misc/%s_rejectedPayments_%s.html" % (districtName.upper(),fullfinyear)
      logger.info(url)
      logger.info(filename) 
      query="update districtStatus set rejectedPaymentCrawlAttemptDate=NOW() where fullDistrictCode='%s'" % fullDistrictCode
      cur.execute(query)
      r=requests.get(url)
      myhtml=r.text
      if "Narration" in myhtml:
        writeFile(filenameRaw,myhtml)
        logger.info(filename) 
#       htmlsoup=BeautifulSoup(myhtml,"html")
#       table=htmlsoup.find('table',id="ctl00_ContentPlaceHolder1_gridData2")
#       title="%s-%s-%s Rejected Payments" % (stateName,districtName,fullfinyear)
#       outhtml=''
#       outhtml+=rewriteRejectedTable(table,"rejectedTable")
#       outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
#       writeFile(filename,outhtml)
        query="update districtStatus set rejectedPaymentCrawlDate=NOW() where fullDistrictCode='%s'" % fullDistrictCode
        cur.execute(query) 
  if args['process']: 
    query="select d.fullDistrictCode,d.crawlIP,d.stateCode,d.stateName,d.rawDistrictName,d.districtName from districts d,districtStatus ds where d.fullDistrictCode=ds.fullDistrictCode  and rejectedPaymentCrawlDate is not NULL and rejectedPaymentProcessDate is NULL %s order by ds.rejectedPaymentCrawlAttemptDate %s " % (additionalFilters,limitString)
    logger.info(query)
    cur.execute(query)
    results=cur.fetchall()
    for row in results:
      [fullDistrictCode,crawlIP,stateCode,stateName,rawDistrictName,districtName] = row
      filepath=nregaWebDir.replace("stateName",stateName.upper()).replace("districtName",districtName.upper())
      filenameRaw=filepath+"/misc/%s_rejectedPayments_%s_orig.html" % (districtName.upper(),fullfinyear)
      filenameCSV=tempDir+"/RejectedPayments/%s_%s_rejectedPayments_%s.csv" % (stateName.upper(),districtName.upper(),fullfinyear)

      logger.info(filenameRaw)
      if os.path.isfile(filenameRaw):  
        logger.info("File Exists")
        f=open(filenameRaw,"rb")
        myhtml=f.read()
        htmlsoup=BeautifulSoup(myhtml,"html")
        table=htmlsoup.find('table',id="ctl00_ContentPlaceHolder1_gridData2")
        rows=table.findAll("tr")
        outString=''
        for eachRow in rows:
          if "Green" in str(eachRow):
             className="green"
          elif "Yellow" in str(eachRow):
             className="yellow"
          elif "Blue" in str(eachRow):
             className="blue"
          else:
             className="red"
          thCols=eachRow.findAll('th')
          if len(thCols) > 1:
           for eachTD in thCols:
             outString+='%s,' % eachTD.text
           outString+='\n'
       
          tdCols=eachRow.findAll('td')
          if len(tdCols) > 1:
            for eachTD in tdCols:
              outString+='%s,' % eachTD.text.replace(",","")
            outString+='%s,' % (className)

        writeFile(filenameCSV,outString)
        query="update districtStatus set rejectedPaymentProcessDate=NOW() where fullDistrictCode='%s' " % fullDistrictCode
        cur.execute(query) 

  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
