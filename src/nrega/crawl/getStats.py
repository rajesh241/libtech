from bs4 import BeautifulSoup
import requests
import os
import sys
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
from wrappers.logger import loggerFetch
from wrappers.db import dbInitialize,dbFinalize
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from crawlSettings import nregaDB,glanceURL 
from crawlSettings import nregaWebDir,nregaRawDataDir,tempDir
from crawlFunctions import alterHTMLTables,writeFile,getjcNumber,NICToSQLDate,getFullFinYear,htmlWrapperLocal,genHTMLHeader,stripTableAttributes,getCenterAligned

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing Jobcards')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-d', '--district', help='District for which you need to Download', required=False)
  parser.add_argument('-fps', '--fullPanchayatCode', help='Full Panchayat Code', required=False)
 
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='District for which you need to Download', required=False)

  args = vars(parser.parse_args())
  return args
def getStateValidation(myhtml):
  bs = BeautifulSoup(myhtml, "html.parser")
  state = bs.find(id='__VIEWSTATE').get('value')
  validation = bs.find(id='__EVENTVALIDATION').get('value')
  return state,validation
def getPostData(state,validation,stateCode=None,fullDistrictCode=None,fullBlockCode=None,fullPanchayatCode=None,submit=None):
  if stateCode is None:
    stateCode=''
  if fullDistrictCode is None:
    fullDistrictCode=''
  if fullBlockCode is None:
    fullBlockCode=''
  if fullPanchayatCode is None:
    fullPanchayatCode=''

  data = {
'__EVENTTARGET':'',
'__EVENTARGUMENT':'',
'__LASTFOCUS':'',
'__VIEWSTATE': state,
'__VIEWSTATEENCRYPTED':'',
'__EVENTVALIDATION':validation,
'ddl_state': stateCode,
'ddl_dist': fullDistrictCode,
'ddl_blk': fullBlockCode,
'ddl_pan': fullPanchayatCode,

    } 
  return data 
def getStatus(cur,logger,url,stateCode,fullDistrictCode,fullBlockCode,fullPanchayatCode):
  httplib2.debuglevel = 1
  h = httplib2.Http('.cache')
  print("URL %s " % url)
  try:
    response = urlopen(url)
    html_source = response.read()
    bs = BeautifulSoup(html_source, "html.parser")
    state = bs.find(id='__VIEWSTATE').get('value')
    validation = bs.find(id='__EVENTVALIDATION').get('value')

    logger.info("State: %s " % state)
    logger.info("Validation: %s " % validation)

    data = {
'__EVENTTARGET':'',
'__EVENTARGUMENT':'',
'__LASTFOCUS':'',
'__VIEWSTATE': state,
'__VIEWSTATEENCRYPTED':'',
'__EVENTVALIDATION':validation,
'ddl_state': stateCode,

    }   #data=getPostData(state,validation,stateCode=stateCode)
    response, content = h.request(url, 'POST', urlencode(data), headers = {'Content-Type': 'application/x-www-form-urlencoded'})
    state,validation=getStateValidation(content)
    logger.info("After putting State: %s " % state)
    logger.info("After Putting State Validation: %s " % validation)
    data = {
'__EVENTTARGET':'',
'__EVENTARGUMENT':'',
'__LASTFOCUS':'',
'__VIEWSTATE': state,
'__VIEWSTATEENCRYPTED':'',
'__EVENTVALIDATION':validation,
'ddl_state': stateCode,
'ddl_dist': fullDistrictCode,

    }
    response, content = h.request(url, 'POST', urlencode(data), headers = {'Content-Type': 'application/x-www-form-urlencoded'})
    state,validation=getStateValidation(content)


    data = {
'__EVENTTARGET':'',
'__EVENTARGUMENT':'',
'__LASTFOCUS':'',
'__VIEWSTATE': state,
'__VIEWSTATEENCRYPTED':'',
'__EVENTVALIDATION':validation,
'ddl_state': stateCode,
'ddl_dist': fullDistrictCode,
'ddl_blk': fullBlockCode,

    }
    response, content = h.request(url, 'POST', urlencode(data), headers = {'Content-Type': 'application/x-www-form-urlencoded'})
    state,validation=getStateValidation(content)

    data = {
'__EVENTTARGET':'',
'__EVENTARGUMENT':'',
'__LASTFOCUS':'',
'__VIEWSTATE': state,
'__VIEWSTATEENCRYPTED':'',
'__EVENTVALIDATION':validation,
'ddl_state': stateCode,
'ddl_dist': fullDistrictCode,
'ddl_blk': fullBlockCode,
'ddl_pan': fullPanchayatCode,
'btproceed' : 'View Detail',

    } 
    response, content = h.request(url, 'POST', urlencode(data), headers = {'Content-Type': 'application/x-www-form-urlencoded'})
    state,validation=getStateValidation(content)

  except:
    response={'status': '404'}
    content=''

  return response,content


 

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("BEGIN PROCESSING...")
  limitString=''
  if args['limit']:
    limitString=" limit %s " % args['limit']
  additionalFilters=''
  if args['district']:
    additionalFilters+= " and p.districtName='%s' " % args['district']
  if args['fullPanchayatCode']:
    additionalFilters= " and p.fullPanchayatCode='%s' " % args['fullPanchayatCode']
  db = dbInitialize(db=nregaDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  

  query="select p.stateCode,p.districtCode,p.blockCode,p.panchayatCode,p.stateName,p.districtName,p.rawBlockName,p.panchayatName,p.fullPanchayatCode,p.stateShortCode,p.crawlIP,p.fullBlockCode from panchayats p,panchayatStatus ps where p.fullPanchayatCode=ps.fullPanchayatCode and p.isRequired=1 and ( (TIMESTAMPDIFF(DAY, ps.jobcardCrawlDate, now()) > 7) or ps.jobcardCrawlDate is NULL)  %s order by ps.jobcardCrawlDate,fullPanchayatCode %s" % (additionalFilters,limitString)
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    [stateCode,districtCode,blockCode,panchayatCode,stateName,districtName,blockName,panchayatName,fullPanchayatCode,stateShortCode,crawlIP,fullBlockCode]=row
    logger.info("Processing statName: %s, districtName: %s, blockName: %s, panchayatName : %s " % (stateName,districtName,blockName,panchayatName))
  fullDistrictCode=stateCode+districtCode 
  filepath=nregaWebDir.replace("stateName",stateName.upper()).replace("districtName",districtName.upper())
  filename=filepath+blockName.upper()+"/%s/%s_stats.html" % (panchayatName.upper(),panchayatName.upper())
  logger.info("filename: %s " % filename)
  url="http://mnregaweb4.nic.in/netnrega/all_lvl_details_new.aspx?panchayat_code=%s&panchayat_name=%s&block_code=%s&block_name=%s&district_code=%s&district_name=%s&state_code=%s&state_name=%s&page=p&fin_year=2015-2016" % (fullPanchayatCode,panchayatName,fullBlockCode,blockName,fullDistrictCode,districtName,stateCode,stateName)
  logger.info(url)
 # htmlresponse,myhtml=getStatus(cur,logger,glanceURL,stateCode,fullDistrictCode,fullBlockCode,fullPanchayatCode)
  
  httplib2.debuglevel = 1
  h = httplib2.Http('.cache')
  htmlresponse, myhtml = h.request(url)
  if htmlresponse['status'] == '200':
    logger.info("File Downloaded SuccessFully")
    if not os.path.exists(os.path.dirname(filename)):
      os.makedirs(os.path.dirname(filename))
    myfile = open(filename, "wb")
    try:
      myfile.write(myhtml.encode("UTF-8"))
    except:
      myfile.write(myhtml)
 
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
