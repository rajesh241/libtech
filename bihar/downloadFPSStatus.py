from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
import time
import re
import sys
import datetime
from MySQLdb import OperationalError
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../includes/')
sys.path.insert(0, fileDir+'/../')
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
#sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery
from biharSettings import pdsDataDir
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Populate Pds SHop codes from csv File')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  #parser.add_argument('-y', '--year', help='Year for which PDS needs to be downloaded', required=True)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-limit', '--limit', help='limit the number of shops that you want to download', required=False)
  parser.add_argument('-fps', '--fpsCode', help='Enter the FPS code of shop that you want to download data for', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  monthLabels=['0','JAN','FEB','MAR','APR','MAY','JUNE','JULY','AUG','SEP','OCT','NOV','DEC']
  now = datetime.datetime.now()
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
  logger.info("Current Year: %s Current Month: %s " %(str(now.year),str(now.month)))
 # inyear=args['year']
  
  #logger.info(inyear)


  if args['limit']:
    limitString=" limit %s " % (str(args['limit']))
  else:
    limitString="  "
  additionalFilters=""
  if args['fpsCode']:
    additionalFilters=" where fpsCode='%s' " % (args['fpsCode'])
  display = displayInitialize(args['visible'])
  driver = driverInitialize(args['browser'])
 
  #Start Program here
  years=['2015','2016']
  years=['2016']
  for inyear in years:
    base_url = "http://sfc.bihar.gov.in/"
   
    query="select id,distCode,blockCode,fpsCode,distName,blockName,fpsName from pdsShops order by downloadAttemptDate %s %s " % (additionalFilters,limitString)
    logger.info(query)
    cur.execute(query)
    results=cur.fetchall()
    for row in results:
      rowid=str(row[0])
      distCode=row[1]
      blockCode=row[2]
      fpsCode=row[3]
      distName=row[4]
      blockName=row[5]
      fpsName=row[6]
      logger.info("disCode:%s   blockCode:%s  fpsCode:%s  distName:%s  blockName:%s  shopName:%s " % (distCode,blockCode,fpsCode,distName,blockName,fpsName))
      query="update pdsShops set downloadAttemptDate=NOW() where id=%s" % (rowid)
      cur.execute(query)
      month=0
      driver.get("http://sfc.bihar.gov.in/login.htm")
      driver.get(base_url + "/fpshopsSummaryDetails.htm")
      while month < 12:
        month=month+1
        if ( (now.year > int(inyear)) or ((now.year == int(inyear)) and (now.month >= month)) ):
          logger.info("Year: %s   Month: %s " % (str(inyear),str(month)))
   
          startDownload=0
          whereClause=" psd.distCode='%s' and psd.blockCode='%s' and psd.fpsCode='%s' and psd.fpsMonth='%s' and psd.fpsYear='%s' " % (distCode,blockCode,fpsCode,str(month),str(inyear))
          query="select isDownloaded from pdsShopsDownloadStatus psd where %s" %(whereClause)
         # logger.info(query)
          cur.execute(query)
          if cur.rowcount == 0:
            query="insert into pdsShopsDownloadStatus (distCode,blockCode,fpsCode,fpsMonth,fpsYear) values ('%s','%s','%s','%s','%s')" % (distCode,blockCode,fpsCode,str(month),str(inyear))
            #logger.info(query)
            cur.execute(query)
            startDownload=1
          else:
            row=cur.fetchone()
            isDownloaded=row[0]
            if isDownloaded == 0:
              startDownload=1
              
          if startDownload==1:
            logger.info("THE data would be downloaded") 
            Select(driver.find_element_by_id("year")).select_by_visible_text(inyear)
            time.sleep(2)
            Select(driver.find_element_by_id("month")).select_by_value(str(month))
            time.sleep(2)
            Select(driver.find_element_by_id("district_id")).select_by_value(distCode)
            time.sleep(2)
            Select(driver.find_element_by_id("block_id")).select_by_value(blockCode)
            time.sleep(2)
            Select(driver.find_element_by_id("fpshop_id")).select_by_value(fpsCode)
            driver.find_element_by_name("button").click()
            time.sleep(5)
   
            fpsHtml = driver.page_source # Saving the result page's source codes
            fpsSoup=BeautifulSoup(fpsHtml,"lxml")
            tablehtml=''
            isDownloaded=0
            tables=fpsSoup.findAll('table',{"class" : "newFormTheme"})
            for table1 in tables:
              isDownloaded=1
              logger.info("FOUND THE TABLE")
              tablehtml+=str(table1)
            #If table has been found we would make isDownloaded=1
            if isDownloaded == 1:
              query="update pdsShopsDownloadStatus psd set isDownloaded=1,downloadAttemptDate=NOW() where %s " % whereClause
              #logger.info(query)
              cur.execute(query)
   
   
            myhtml=''
            myhtml+=  getCenterAligned('<h3 style="color:green"> %s - %s</h3>'  % (monthLabels[int(month)],inyear))
            query="select p.distName,p.distCode,p.blockName,p.blockCode,p.fpsCode,psd.downloadAttemptDate downloadDate from pdsShops p, pdsShopsDownloadStatus psd where p.distCode=psd.distCode and p.blockCode=psd.blockCode and p.fpsCode=psd.fpsCode and %s " % whereClause
            queryTable=bsQuery2HtmlV2(cur,query) 
            queryTable=queryTable.replace("<tr>","<tr class='info'>")
            myhtml+=queryTable
            myhtml+="</br>"
            myhtml+="</br>"
            myhtml+="</br>"
            tablehtml=tablehtml.replace("newFormTheme","newFormTheme table table-striped")
            tablehtml=tablehtml.replace("<tr>","<tr class='success'>")
            myhtml+=tablehtml
            #logger.info(query)
            myhtml=htmlWrapperLocal(title="PDS Details", head='<h1 aling="center">'+fpsName+'</h1>', body=myhtml)
            myhtml = myhtml.encode("UTF-8")
            #Writing my html to the file
            myfilename="%s/%s/%s/%s/%s/%s.html" % (pdsDataDir,str(inyear),monthLabels[int(month)],distName.upper(),blockName.upper(),fpsCode+"_"+fpsName)
            myfilename=myfilename.replace(" ","_")
            logger.info(myfilename)
            if not os.path.exists(os.path.dirname(myfilename)):
              os.makedirs(os.path.dirname(myfilename))
            h = open(myfilename, 'w')
            h.write(myhtml)
            h.close()
   
  # End program here

  driverFinalize(driver)
  displayFinalize(display)
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors


  
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()
