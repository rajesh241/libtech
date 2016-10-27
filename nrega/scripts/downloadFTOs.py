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
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import writeFile,getFullFinYear,singleRowQuery
from nregaSettings import nregaRawDataDir
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable
from crawlFunctions import getDistrictParams
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
    additionalFilters=" and b.blockCode='%s' " % args['blockCode']
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)
  filepath=nregaRawDataDir.replace("districtName",districtName.lower())
  fullfinyear=getFullFinYear(finyear)
  display = displayInitialize(args['visible'])
  driver = driverInitialize(args['browser'])
  url="http://164.100.129.6/netnrega/nregasearch1.aspx"
  driver.get(url)
  time.sleep(2)

  query="select f.id,f.ftoNo,b.name,b.blockCode from ftoDetails f,blocks b where f.blockCode=b.blockCode and ( (f.isDownloaded=0) or ((f.isComplete=0 and TIMESTAMPDIFF(HOUR, f.downloadAttemptDate, now()) > 48 ) )) and finyear='%s' %s order by isDownloaded %s " % (finyear,additionalFilters,limitString)
  logger.info(query)
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    rowid=str(row[0])
    ftoNo=row[1] 
    blockName=row[2]
    blockCode=row[3]
    if ftoNo != '':
      ftoPrefix=stateShortCode+stateCode+districtCode+blockCode
      logger.info(ftoNo)
      maintab = driver.current_window_handle
      Select(driver.find_element_by_id("ddl_search")).select_by_visible_text("Fund Transfer Order (FTO)")
      driver.find_element_by_css_selector("option[value=\"FTO\"]").click()
      Select(driver.find_element_by_id("ddl_state")).select_by_visible_text(stateName.upper())
      myvalue='value="%s"' % stateCode
      #driver.find_element_by_css_selector("option[value=\"33\"]").click()
      driver.find_element_by_css_selector("option[%s]" % myvalue).click()
      Select(driver.find_element_by_id("ddl_district")).select_by_visible_text(districtName.upper())
      myvalue='value="%s"' % (stateCode+districtCode)
      #driver.find_element_by_css_selector("option[value=\"3305\"]").click()
      driver.find_element_by_css_selector("option[%s]" % myvalue).click()
      driver.find_element_by_id("txt_keyword2").clear()
      driver.find_element_by_id("txt_keyword2").send_keys(ftoNo)
      driver.find_element_by_id("btn_go").click()
      #time.sleep(30)
      logger.info("Currently the number of active tabs are %s" % str(len(driver.window_handles))) 
      if len(driver.window_handles) > 1:
        logger.info("There are multiple tabs")
        driver.switch_to_window(driver.window_handles[1])

        #htmlsource = driver.page_source
        #logger.info(htmlsource)
        # ERROR: Caught exception [ERROR: Unsupported command [waitForPopUp |  | 30000]]
        # ERROR: Caught exception [ERROR: Unsupported command [selectWindow | null | ]]
        driver.find_element_by_link_text(ftoNo).click()
        if ftoPrefix in ftoNo:
          ftoSelect="%s(Block=%s)" % (ftoNo,blockName)
        else:
          ftoSelect=ftoNo
        logger.info("FTO Select = %s " % ftoSelect)
        Select(driver.find_element_by_id("ctl00_ContentPlaceHolder1_Ddfto")).select_by_visible_text(ftoSelect)
        driver.find_element_by_css_selector("option[value="+ftoNo+"]").click()
        htmlsource = driver.page_source
        htmlsource=htmlsource.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
        success=0
        isPopulatedString=''
        writeFile("/home/libtech/webroot/nreganic.libtech.info/temp/"+ftoNo+".html",htmlsource)
        if "FTO_Acc_signed_dt_p2w" in htmlsource:
          filename=filepath+blockName.upper()+"/FTO/"+fullfinyear+"/"+ftoNo+".html"
          logger.info(filename)
          writeFile("/home/libtech/webroot/nreganic.libtech.info/temp/"+ftoNo+".html",htmlsource)
          writeFile(filename,htmlsource)
          success=1
          isPopulatedString="isPopulated=0,"
        query="update ftoDetails set isDownloaded=%s,%sdownloadAttemptDate=NOW()  where id=%s" %(str(success),str(isPopulatedString),str(rowid))
        logger.info(query)
        cur.execute(query)
        driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')
        driver.switch_to_window(maintab) 
          

  driverFinalize(driver)
  displayFinalize(display)
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()






#import csv
#from bs4 import BeautifulSoup
#import requests
#import MySQLdb
#import os
#import sys
#import importlib
#fileDir=os.path.dirname(os.path.abspath(__file__))
#sys.path.insert(0, fileDir+'/../../includes/')
#sys.path.insert(0, fileDir+'/../../')
#from nregaSettings import nregaRawDataDir
#from libtechFunctions import writeFile,getFullFinYear,singleRowQuery
##Connect to MySQL Database
#from wrappers.logger import loggerFetch
#from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
#from wrappers.db import dbInitialize,dbFinalize
#sys.path.insert(0, fileDir+'/../crawlDistricts/')
#from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable
#from crawlFunctions import alterFTOHTML
#from crawlFunctions import getDistrictParams
#def argsFetch():
#  '''
#  Paser for the argument list that returns the args list
#  '''
#  import argparse
#
#  parser = argparse.ArgumentParser(description='Script for Downloading FTOs')
#  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
#  parser.add_argument('-limit', '--limit', help='Limit the number of ftos to be downloaded', required=False)
#  parser.add_argument('-f', '--finyear', help='Download musters for that finyear', required=True)
#  parser.add_argument('-d', '--district', help='District for which you need to Download', required=True)
#
#  args = vars(parser.parse_args())
#  return args
#
#def main():
#  args = argsFetch()
#  logger = loggerFetch(args.get('log_level'))
#  logger.info('args: %s', str(args))
#
#  logger.info("BEGIN PROCESSING...")
#
#  limitString=''
#  if args['limit']:
#    limitString=' limit '+args['limit']
#  if args['district']:
#    districtName=args['district']
# 
#  logger.info("DistrictName "+districtName)
#  finyear=args['finyear']
#  
#  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
#  cur=db.cursor()
#  db.autocommit(True)
#  #Query to set up Database to read Hindi Characters
#  query="SET NAMES utf8"
#  cur.execute(query)
#  logger.info("finyear "+finyear)
#  fullFinyear=getFullFinYear(finyear) 
#  crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)
##Query to get all the blocks
#
#
#
#  ftorawfilepath=nregaRawDataDir.replace("districtName",districtName.lower())
#
#  #ftorawfilepath=htmlRawDir+"/"+districtName.upper()+"/"
##ftofilepath="/home/libtech/libtechdata/CHATTISGARH/"+districtName+"/"
#  query="select b.name,f.ftoNo,f.blockCode,f.finyear,f.id from ftoDetails f,blocks b where f.isDownloaded=0 and f.finyear='%s' and f.blockCode=b.blockCode   %s;" % (finyear,limitString)
#  logger.info(query)
##query="select b.name,f.ftoNo,f.stateCode,f.districtCode,f.blockCode,f.finyear,f.id from ftoDetails f,blocks b where f.isDownloaded=0 and f.blockCode=b.blockCode and f.stateCode=b.stateCode and f.districtCode=b.districtCode and b.blockCode='003';"
#  cur.execute(query)
#  logger.info("Number of ftos to be downloaded is "+str(cur.rowcount))
#  results = cur.fetchall()
#  for row in results:
#    blockName=row[0]
#    ftono=row[1]
#    blockCode=row[2]
#    finyear=row[3]
#    ftoid=row[4]
#    fullBlockCode=stateCode+districtCode+blockCode
#    fullDistrictCode=stateCode+districtCode
#    tableHTML=''
#    classAtt='id = "basic" class = " table table-striped"' 
#    tableHTML+='<table %s">' % classAtt
#    tableHTML+="<tr><th> %s </th><td> %s </td></tr>" %("District Name",districtName.upper())
#    tableHTML+="<tr><th> %s </th><td> %s </td></tr>" %("Block Name",blockName.upper())
#    tableHTML+="<tr><th> %s </th><td> %s </td></tr>" %("FTO NO",ftono)
#    logger.info(stateCode+districtCode+blockCode+blockName)
#    fullfinyear=getFullFinYear(finyear)
#    url="http://"+crawlIP+"/netnrega/FTO/fto_trasction_dtl.aspx?page=p&rptblk=t&state_code="+stateCode+"&state_name="+stateName.upper()+"&district_code="+fullDistrictCode+"&district_name="+districtName.upper()+"&block_code="+fullBlockCode+"&block_name="+blockName+"&flg=W&fin_year="+fullfinyear+"&fto_no="+ftono
#    logger.info(str(ftoid)+"   "+fullfinyear+"  "+ftono)
#    logger.info(url)
#    #ftofilename=ftofilepath+blockName.upper()+"/FTO/"+fullfinyear+"/"+ftono+".html"
#    #logger.info(ftofilename)
#    r=requests.get(url)
#    r=requests.get(url)
#    inhtml=r.text
#    ftorawfilename=ftorawfilepath+blockName.upper()+"/FTO/"+fullfinyear+"/"+ftono+".html"
#    writeFile(ftorawfilename,inhtml)
#    query="update ftoDetails set isDownloaded=1 where id="+str(ftoid)
#    cur.execute(query)
##   errorflag,outhtml=alterFTOHTML(inhtml)
##   if errorflag==0:
##     logger.info("FTO Download Success Updating the Status")
##     ftohtml=''
##     ftohtml+=tableHTML
##     ftohtml+=outhtml
##     ftohtml=htmlWrapperLocal(title="FTO Details", head='<h1 aling="center">'+ftono+'</h1>', body=ftohtml)
##     writeFile(ftofilename,ftohtml)
##     query="update ftoDetails set isDownloaded=1 where id="+str(ftoid)
##     cur.execute(query)
#
#
#  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
#  logger.info("...END PROCESSING")     
#  exit(0)
#if __name__ == '__main__':
#  main()
