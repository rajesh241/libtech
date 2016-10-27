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
from nregaSettings import nregaRawDataDir,searchIP
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable
from crawlFunctions import getDistrictParams
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script to Download WageLists')
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
  fullDistrictCode=stateCode+districtCode
  display = displayInitialize(args['visible'])
  driver = driverInitialize(args['browser'])
  url="http://164.100.129.6/netnrega/nregasearch1.aspx"
  driver.get(url)
  time.sleep(22)
  htmlsource = driver.page_source
  writeFile("/home/libtech/webroot/nreganic.libtech.info/temp/a.html",htmlsource)

  query="select w.id,w.wagelistNo,b.name from wagelists w,blocks b where w.blockCode=b.blockCode and ( (w.isDownloaded=0) or (w.isComplete=0 and TIMESTAMPDIFF(HOUR, w.downloadAttemptDate, now()) > 48 )) and finyear='%s' %s order by w.isDownloaded %s " % (finyear,additionalFilters,limitString)
  query="select w.id,w.wagelistNo,b.name from wagelists w,blocks b where w.blockCode=b.blockCode and w.id=1 and finyear='%s' %s order by w.isDownloaded limit 1 " % (finyear,additionalFilters)
  logger.info(query)
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    rowid=str(row[0])
    wagelistNo=row[1] 
    blockName=row[2]
    logger.info("Same WagelistNo %s " % wagelistNo)
    if wagelistNo != '':
     # logger.info(wagelistNo)
      maintab = driver.current_window_handle
      Select(driver.find_element_by_id("ddl_search")).select_by_visible_text("WageList")
      driver.find_element_by_css_selector("option[value=\"WageList\"]").click()
      Select(driver.find_element_by_id("ddl_state")).select_by_visible_text(stateName.upper())
      myvalue='value="%s"' % stateCode
      #driver.find_element_by_css_selector("option[value=\"33\"]").click()
      driver.find_element_by_css_selector("option[%s]" % myvalue).click()
      Select(driver.find_element_by_id("ddl_district")).select_by_visible_text(districtName.upper())
      myvalue='value="%s"' % (stateCode+districtCode)
      #driver.find_element_by_css_selector("option[value=\"3305\"]").click()
      driver.find_element_by_css_selector("option[%s]" % myvalue).click()
      driver.find_element_by_id("txt_keyword2").clear()
      driver.find_element_by_id("txt_keyword2").send_keys(wagelistNo)
      driver.find_element_by_id("btn_go").click()
      time.sleep(30)
      logger.info("Currently the number of active tabs are %s" % str(len(driver.window_handles))) 
      if len(driver.window_handles) > 1:
        logger.info("There are multiple tabs")
        driver.switch_to_window(driver.window_handles[1])

        #htmlsource = driver.page_source
        #logger.info(htmlsource)
        # ERROR: Caught exception [ERROR: Unsupported command [waitForPopUp |  | 30000]]
        # ERROR: Caught exception [ERROR: Unsupported command [selectWindow | null | ]]
        elems = driver.find_elements_by_xpath("//a[@href]")
        if len(elems) > 0:
          query="select w.id,w.wagelistNo,b.name,b.blockCode from wagelists w,blocks b where w.blockCode=b.blockCode and ( (w.isDownloaded=0) or (w.isComplete=0 and TIMESTAMPDIFF(HOUR, w.downloadAttemptDate, now()) > 48 )) and finyear='%s' %s order by w.isDownloaded %s " % (finyear,additionalFilters,limitString)
          cur.execute(query)
          results1=cur.fetchall()
          for row1 in results1:
            rowid=str(row1[0])
            wagelistNo=row1[1] 
            blockName=row1[2]
            blockCode=row1[3]
            jobcardPrefix="%s-%s-%s-" % (stateShortCode,districtCode,blockCode)
            logger.info("Jobcard Prefix : %s " % jobcardPrefix)
            fullBlockCode=stateCode+districtCode+blockCode
            if wagelistNo != '':
              logger.info(wagelistNo)
              wurl="http://%s/netnrega/srch_wg_dtl.aspx?state_code=&district_code=%s&state_name=%s&district_name=%s&block_code=%s&wg_no=%s&short_name=%s&fin_year=%s&mode=wg" % (searchIP,fullDistrictCode,stateName.upper(),districtName.upper(),fullBlockCode,wagelistNo,stateShortCode,fullfinyear)
              logger.info("URL: %s " % wurl)
              driver.get(wurl)
              htmlsource = driver.page_source
              htmlsource=htmlsource.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
              success=0
              isPopulatedString=''
              if ("WageList Agency Code" in htmlsource) and (jobcardPrefix in htmlsource):
                filename=filepath+blockName.upper()+"/WAGELIST/"+fullfinyear+"/"+wagelistNo+".html"
                logger.info(filename)
                writeFile("/home/libtech/webroot/nreganic.libtech.info/temp/"+wagelistNo+".html",htmlsource)
                writeFile(filename,htmlsource)
                success=1
                isPopulatedString="isProcessed=0,"
              query="update wagelists set isDownloaded=%s,%sdownloadAttemptDate=NOW()  where id=%s" %(str(success),isPopulatedString,str(rowid))
              logger.info(query)
              cur.execute(query)
           
        # elem=driver.find_element_by_link_text(wagelistNo)
        # hrefLink=str(elem.get_attribute("href"))
        # logger.info(hrefLink)
        # driver.get(hrefLink)
        # htmlsource = driver.page_source
        # htmlsource=htmlsource.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
        # success=0
        # isPopulatedString=''
        # if "WageList Agency Code" in htmlsource:
        #   filename=filepath+blockName.upper()+"/WAGELIST/"+fullfinyear+"/"+wagelistNo+".html"
        #   logger.info(filename)
        #   writeFile("/home/libtech/webroot/nreganic.libtech.info/temp/"+wagelistNo+".html",htmlsource)
        #   writeFile(filename,htmlsource)
        #   success=1
        #   isPopulatedString="isProcessed=0,"
        # query="update wagelists set isDownloaded=%s,%sdownloadAttemptDate=NOW()  where id=%s" %(str(success),isPopulatedString,str(rowid))
        # logger.info(query)
        # cur.execute(query)
        driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')
        driver.switch_to_window(maintab) 
          

  driverFinalize(driver)
  displayFinalize(display)
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()

