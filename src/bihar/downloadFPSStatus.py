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
from urllib import urlencode
import httplib2
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
  parser.add_argument('-d', '--distCode', help='Enter the Dist code of district that you want to download data for', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  httplib2.debuglevel = 1
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
  limitString=''
  if args['limit']:
    limitString=' limit %s ' % args['limit']
  
  
  query="select pd.id,pd.distCode,pd.blockCode,pd.fpsCode,p.distName,p.blockName,p.fpsName,pd.fpsMonth,pd.fpsYear from pdsShops p, pdsShopsDownloadStatus pd where pd.distCode=p.distCode and pd.blockCode=p.blockCode and pd.fpsCode=p.fpsCode and pd.isDownloaded=0 and  (pd.statusRemark != 'completeRecord' or pd.statusRemark is NULL ) %s" % (limitString)
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
    fpsMonth=row[7]
    fpsYear=row[8]
    logger.info("disCode:%s   blockCode:%s  fpsCode:%s  distName:%s  blockName:%s  shopName:%s " % (distCode,blockCode,fpsCode,distName,blockName,fpsName))
            
    hlib = httplib2.Http('.cache')
    url = 'http://sfc.bihar.gov.in/fpshopsSummaryDetails.htm'
 
    data = {
     'mode':'searchFPShopDetails',
     'dyna(state_id)':'10',
     'dyna(fpsCode)':'',
     'dyna(scheme_code)':'',
     'dyna(year)':fpsYear,
     'dyna(month)':fpsMonth,
     'dyna(district_id)':distCode,
     'dyna(block_id)':blockCode,
     'dyna(fpshop_id)':fpsCode,
     }
 
    #print(urlencode(data))
    response, fpsHtml = hlib.request(url, 'POST', urlencode(data), headers = {'Content-Type': 'application/x-www-form-urlencoded'})
 
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
      query="update pdsShopsDownloadStatus psd set isDownloaded=1,downloadAttemptDate=NOW() where id=%s" % (rowid)
      #logger.info(query)
      cur.execute(query)
      myhtml=''
      myhtml+=  getCenterAligned('<h3 style="color:green"> %s - %s</h3>'  % (monthLabels[int(fpsMonth)],fpsYear))
      query="select p.distName,p.distCode,p.blockName,p.blockCode,p.fpsCode,psd.downloadAttemptDate downloadDate from pdsShops p, pdsShopsDownloadStatus psd where psd.distCode=p.distCode and psd.blockCode=p.blockCode and psd.fpsCode=p.fpsCode and psd.id=%s" % rowid
      logger.info(query)
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
      myfilename="%s/%s/%s/%s/%s/%s.html" % (pdsDataDir,str(fpsYear),monthLabels[int(fpsMonth)],distName.upper(),blockName.upper(),fpsCode+"_"+fpsName)
      myfilename=myfilename.replace(" ","_")
      logger.info(myfilename)
      if not os.path.exists(os.path.dirname(myfilename)):
        os.makedirs(os.path.dirname(myfilename))
      h = open(myfilename, 'w')
      h.write(myhtml)
      h.close()

  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)

# httplib2.debuglevel = 1
# monthLabels=['0','JAN','FEB','MAR','APR','MAY','JUNE','JULY','AUG','SEP','OCT','NOV','DEC']
# now = datetime.datetime.now()
# args = argsFetch()
# logger = loggerFetch(args.get('log_level'))
# logger.info('args: %s', str(args))
#
# logger.info("BEGIN PROCESSING...")
# db = dbInitialize(db="biharPDS", charset="utf8")  # The rest is updated automatically in the function
# cur=db.cursor()
# db.autocommit(True)
# #Query to set up Database to read Hindi Characters
# query="SET NAMES utf8"
# cur.execute(query)
# logger.info("Current Year: %s Current Month: %s " %(str(now.year),str(now.month)))
## inyear=args['year']
# 
# #logger.info(inyear)
#
#
# if args['limit']:
#   limitString=" limit %s " % (str(args['limit']))
# else:
#   limitString="  "
# additionalFilters=""
# if args['fpsCode']:
#   additionalFilters=" where fpsCode='%s' " % (args['fpsCode'])
# if args['distCode']:
#   additionalFilters=" where distCode='%s' " % (args['distCode'])
# query="select pd.id,pd.distCode,pd.blockCode,pd.fpsCode,p.distName,p.blockName,p.fpsName,pd.fpsMonth,pd.fpsYear from pdsShops p, pdsShopsDownloadStatus pd where pd.distCode=p.distCode and pd.blockCode=p.blockCode and pd.fpsCode=p.fpsCode and (pd.statusRemark != 'completeRecord' or pd.statusRemark is NULL )"
# logger.info(query)
# cur.execute(query)
# results=cur.fetchall()
# for row in results:
#   rowid=str(row[0	])
#   distCode=row[1]
#   blockCode=row[2]
#   fpsCode=row[3]
#   distName=row[4]
#   blockName=row[5]
#   fpsName=row[6]
#   fpsMonth=row[7]
#   fpsYear=row[8]
#   logger.info("disCode:%s   blockCode:%s  fpsCode:%s  distName:%s  blockName:%s  shopName:%s " % (distCode,blockCode,fpsCode,distName,blockName,fpsName))
#           
#   hlib = httplib2.Http('.cache')
#   url = 'http://sfc.bihar.gov.in/fpshopsSummaryDetails.htm'
#
#   data = {
#    'mode':'searchFPShopDetails',
#    'dyna(state_id)':'10',
#    'dyna(fpsCode)':'',
#    'dyna(scheme_code)':'',
#    'dyna(year)':fpsYear,
#    'dyna(month)':fpsMonth,
#    'dyna(district_id)':distCode,
#    'dyna(block_id)':blockCode,
#    'dyna(fpshop_id)':fpsCode,
#    }
#
#   #print(urlencode(data))
#   response, fpsHtml = hlib.request(url, 'POST', urlencode(data), headers = {'Content-Type': 'application/x-www-form-urlencoded'})
#
#   fpsSoup=BeautifulSoup(fpsHtml,"lxml")
#   tablehtml=''
#   isDownloaded=0
#   tables=fpsSoup.findAll('table',{"class" : "newFormTheme"})
#   for table1 in tables:
#     isDownloaded=1
#     logger.info("FOUND THE TABLE")
#     tablehtml+=str(table1)
#   #If table has been found we would make isDownloaded=1
#   if isDownloaded == 1:
#     query="update pdsShopsDownloadStatus psd set isDownloaded=1,downloadAttemptDate=NOW() where id=%s" % (rowid)
#     #logger.info(query)
#     cur.execute(query)
#
#
#   myhtml=''
#   myhtml+=  getCenterAligned('<h3 style="color:green"> %s - %s</h3>'  % (monthLabels[int(fpsMonth)],inyear))
#   query="select p.distName,p.distCode,p.blockName,p.blockCode,p.fpsCode,psd.downloadAttemptDate downloadDate from pdsShops p, pdsShopsDownloadStatus psd where p.distCode=psd.distCode and p.blockCode=psd.blockCode and p.fpsCode=psd.fpsCode and %s " % whereClause
#   queryTable=bsQuery2HtmlV2(cur,query) 
#   queryTable=queryTable.replace("<tr>","<tr class='info'>")
#   myhtml+=queryTable
#   myhtml+="</br>"
#   myhtml+="</br>"
#   myhtml+="</br>"
#   tablehtml=tablehtml.replace("newFormTheme","newFormTheme table table-striped")
#   tablehtml=tablehtml.replace("<tr>","<tr class='success'>")
#   myhtml+=tablehtml
#   #logger.info(query)
#   myhtml=htmlWrapperLocal(title="PDS Details", head='<h1 aling="center">'+fpsName+'</h1>', body=myhtml)
#   myhtml = myhtml.encode("UTF-8")
#   #Writing my html to the file
#   myfilename="%s/%s/%s/%s/%s/%s.html" % (pdsDataDir,str(inyear),monthLabels[int(fpsMonth)],distName.upper(),blockName.upper(),fpsCode+"_"+fpsName)
#   myfilename=myfilename.replace(" ","_")
#   logger.info(myfilename)
#   if not os.path.exists(os.path.dirname(myfilename)):
#     os.makedirs(os.path.dirname(myfilename))
#   h = open(myfilename, 'w')
#   h.write(myhtml)
#   h.close()
#
# # End program here
#
# #driverFinalize(driver)
# #displayFinalize(display)
# dbFinalize(db) # Make sure you put this if there are other exit paths or errors
# logger.info("...END PROCESSING")     
# exit(0)


if __name__ == '__main__':
  main()
