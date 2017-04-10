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
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import writeFile3,getFullFinYear,singleRowQuery
from nregaSettings import nregaRawDataDir,ftoSearchURL
from crawlFunctions import getDistrictParams
from urllib.request import urlopen   # REVIST
from urllib.parse import urlencode
import httplib2

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script to Download FTOs')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-f', '--finyear', help='Download musters for that finyear', required=True)
  parser.add_argument('-d', '--district', help='District for which you need to Download', required=True)
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-blockCode', '--blockCode', help='BlockCode for  which you need to Download', required=False)
  parser.add_argument('-limit', '--limit', help='Limit the number of panchayats to be processed', required=False)

  args = vars(parser.parse_args())
  return args
def getFTO(fullfinyear,stateCode,ftoNo):
  httplib2.debuglevel = 1
  h = httplib2.Http('.cache')
  url = "http://164.100.129.6/netnrega/fto/fto_status_dtl.aspx?fto_no=%s&fin_year=%s&state_code=%s" % (ftoNo, fullfinyear, stateCode)
  response = urlopen(url)
  html_source = response.read()
  bs = BeautifulSoup(html_source, "html.parser")
  state = bs.find(id='__VIEWSTATE').get('value')
#  logger.info('state[%s]' % state)
  validation = bs.find(id='__EVENTVALIDATION').get('value')
#  logger.info('value[%s]' % validation)
  data = {
    '__EVENTTARGET':'ctl00$ContentPlaceHolder1$Ddfto',
    '__EVENTARGUMENT':'',
    '__LASTFOCUS':'',
    '__VIEWSTATE': state,
    '__VIEWSTATEENCRYPTED':'',
    '__EVENTVALIDATION': validation,
    'ctl00$ContentPlaceHolder1$Ddfin': fullfinyear,
    'ctl00$ContentPlaceHolder1$Ddstate': stateCode,
    'ctl00$ContentPlaceHolder1$Txtfto': ftoNo,
    'ctl00$ContentPlaceHolder1$Ddfto': ftoNo,
  }

  response, content = h.request(url, 'POST', urlencode(data), headers = {'Content-Type': 'application/x-www-form-urlencoded'})

  return response,content

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  districtName=args['district']
  finyear=args['finyear']
  logger.info("DistrictName "+districtName)
  limitString=''
  if args['limit']:
    limitString=" limit %s " % args['limit']
  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  additionalFilters = ''
  if args['blockCode']:
    additionalFilters=" and f.blockCode='%s' " % args['blockCode']
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)
  filepath=nregaRawDataDir.replace("districtName",districtName.lower())
  fullfinyear=getFullFinYear(finyear)

  query="select f.id,f.ftoNo,f.isDistrictFTO,f.blockCode from ftoDetails f where   ( (f.isDownloaded=0) or ((f.isComplete=0 and TIMESTAMPDIFF(HOUR, f.downloadAttemptDate, now()) > 48 ) )) and finyear='%s' %s order by isDownloaded %s " % (finyear,additionalFilters,limitString)
  logger.info(query)
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    rowid=str(row[0])
    ftoNo=row[1] 
    isDistrictFTO=row[2]
    blockCode=row[3]
    if ftoNo != '':
      filename=filepath+"/FTO/"+fullfinyear+"/"+ftoNo+".html"
      if isDistrictFTO == 0:
        query="select name from blocks where blockCode=%s " % blockCode
        cur.execute(query)
        blockrow=cur.fetchone()
        blockName=blockrow[0]
        filename=filepath+blockName.upper()+"/FTO/"+fullfinyear+"/"+ftoNo+".html"
      logger.info("Downloading FTO: %s " % ftoNo)
      htmlresponse,htmlsource = getFTO(fullfinyear,stateCode,ftoNo)
      logger.info("Response = %s " % htmlresponse)
      success=0
      isPopulatedString=''
      if htmlresponse['status'] == '200':
        logger.info("Status is 200")
        isPopulatedString="isPopulated=0,"
        success=1
        writeFile3(filename,htmlsource)
        #writeFile3("/home/libtech/webroot/nreganic.libtech.info/temp/"+ftoNo+".html",htmlsource)
      query="update ftoDetails set isDownloaded=%s,%sdownloadAttemptDate=NOW()  where id=%s" %(str(success),str(isPopulatedString),str(rowid))
      logger.info(query)
      cur.execute(query)

  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()





