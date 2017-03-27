from bs4 import BeautifulSoup
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
import multiprocessing, time
import requests
import MySQLdb
import os
import os.path
import time
import re
import sys
from MySQLdb import OperationalError
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
#sys.path.insert(0, rootdir)
import datetime
from wrappers.logger import loggerFetch
from wrappers.db import dbInitialize,dbFinalize
from crawlSettings import nregaDB,searchIP 
from crawlSettings import nregaWebDir,nregaRawDataDir,tempDir
from crawlFunctions import alterHTMLTables,writeFile,getjcNumber,NICToSQLDate,getFullFinYear,htmlWrapperLocal,genHTMLHeader,stripTableAttributes,getCenterAligned
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing musters')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-f', '--finyear', help='Download musters for that finyear', required=True)
  parser.add_argument('-d', '--district', help='District for which you need to Download', required=False)
  parser.add_argument('-b', '--blockCode', help='BlockCode for  which you need to Download', required=False)
  parser.add_argument('-p', '--panchayatCode', help='panchayatCode for  which you need to Download', required=False)
  parser.add_argument('-br', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-dw', '--downloadWagelists', help='Download Wage Lists', required=False,action='store_const', const=1)
  parser.add_argument('-df', '--downloadFTOs', help='Download FTOs', required=False,action='store_const', const=1)
  parser.add_argument('-limit', '--limit', help='District for which you need to Download', required=False)

  args = vars(parser.parse_args())
  return args

def alterFTO(cur,logger,inhtml,stateName,districtName,blockName,ftoNo,rowid):
  htmlsoup = BeautifulSoup(inhtml, "lxml")
  tables=htmlsoup.findAll('table')
  outhtml=''
  title="%s-%s-%s" % (stateName,districtName,ftoNo)
  #outhtml+=getCenterAligned('<h3 style="color:blue"> %s</h3>' %title )
  firstTable=''
  secondTable=''
  status=0
  for table in tables:
    if "Name of primary Account holder" in str(table):
      logger.info("Found the Beneficiary Table")
      secondTable+=stripTableAttributes(table,"libtechDetails")
      status=1

  if status == 1:
    myspan=htmlsoup.find('span',id="ctl00_ContentPlaceHolder1_lbl_mode")
    paymentMode=myspan.text.lstrip().rstrip()
    myspan=htmlsoup.find('span',id="ctl00_ContentPlaceHolder1_lbl_acc")
    firstSignatoryDateString=myspan.text.lstrip().rstrip()
    myspan=htmlsoup.find('span',id="ctl00_ContentPlaceHolder1_lbl_acc_p2w")
    secondSignatoryDateString=myspan.text.lstrip().rstrip()
    myspan=htmlsoup.find('span',id="ctl00_ContentPlaceHolder1_lbl_cr_proc_p")
    toFinAgencyDateString=myspan.text.lstrip().rstrip()
    logger.info("First Signatory Date: %s" % firstSignatoryDateString)
    logger.info("Second Signatory Date: %s" % secondSignatoryDateString)
    logger.info("To Financial Agency Date: %s" % toFinAgencyDateString)
    logger.info("Payment Mode: %s" % paymentMode)
    query="update ftos set firstSignatoryDate=%s,secondSignatoryDate=%s,bankProcessedDate=%s,paymentMode='%s' where id=%s " % (NICToSQLDate(firstSignatoryDateString),NICToSQLDate(secondSignatoryDateString),NICToSQLDate(toFinAgencyDateString),paymentMode,str(rowid))
 
    cur.execute(query)
    logger.info(query)
    table=htmlsoup.find('table',id='ctl00_ContentPlaceHolder1_tt1')
    firstTable=stripTableAttributes(table,"libtechHeader")
    
  modifiedHTML=outhtml+firstTable+secondTable
  modifiedHTML=htmlWrapperLocal(title=title, head='<h1 aling="center" style="color:blue">'+title+'</h1>', body=modifiedHTML)
  return status,modifiedHTML
def getFTO(fullfinyear,stateCode,ftoNo):
  httplib2.debuglevel = 1
  h = httplib2.Http('.cache')
  url = "http://164.100.129.6/netnrega/fto/fto_status_dtl.aspx?fto_no=%s&fin_year=%s&state_code=%s" % (ftoNo, fullfinyear, stateCode)
  print("FTO URL %s " % url)
  try:
    response = urlopen(url)
    html_source = response.read()
    bs = BeautifulSoup(html_source, "html.parser")
    state = bs.find(id='__VIEWSTATE').get('value')
#    logger.info('state[%s]' % state)
    validation = bs.find(id='__EVENTVALIDATION').get('value')
#    logger.info('value[%s]' % validation)
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
  except:
    response={'status': '404'}
    content=''

  return response,content

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("BEGIN PROCESSING...")
  db = dbInitialize(db=nregaDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =50000
  limitString=" limit %s " % str(limit)
  additionalFilters=''
  if args['district']:
    additionalFilters+= " and b.districtName='%s' " % args['district']
  if args['finyear']:
    additionalFilters+= " and finyear='%s' " % args['finyear'] 
  if args["downloadWagelists"]: 
    display = displayInitialize(args['visible'])
    driver = driverInitialize(args['browser'])
   
    url="http://164.100.129.6/netnrega/nregasearch1.aspx"
    driver.get(url)
    time.sleep(22)
    htmlsource = driver.page_source
    #writeFile("/tmp/a.html",htmlsource)
    stateName="CHHATTISGARH"
    districtName="SURGUJA"
    wagelistNo="3305002062WL005160"
    try:
      maintab = driver.current_window_handle
      Select(driver.find_element_by_id("ddl_search")).select_by_visible_text("WageList")
      driver.find_element_by_css_selector("option[value=\"WageList\"]").click()
      Select(driver.find_element_by_id("ddl_state")).select_by_visible_text(stateName.upper())
      #myvalue='value="%s"' % stateCode
      driver.find_element_by_css_selector("option[value=\"33\"]").click()
     # driver.find_element_by_css_selector("option[%s]" % myvalue).click()
      Select(driver.find_element_by_id("ddl_district")).select_by_visible_text(districtName.upper())
      #myvalue='value="%s"' % (stateCode+districtCode)
      driver.find_element_by_css_selector("option[value=\"3305\"]").click()
      #driver.find_element_by_css_selector("option[%s]" % myvalue).click()
      driver.find_element_by_id("txt_keyword2").clear()
      driver.find_element_by_id("txt_keyword2").send_keys(wagelistNo)
      driver.find_element_by_id("btn_go").click()
      time.sleep(30)
      #logger.info("Currently the number of active tabs are %s" % str(len(driver.window_handles))) 
      error=0
    except:
      error=1
    wurl="http://164.100.129.6/netnrega/srch_wg_dtl.aspx?state_code=&district_code=3305&state_name=CHHATTISGARH&district_name=SURGUJA&block_code=3305002&wg_no=3305002062WL005160&short_name=CH&fin_year=2016-2017&mode=wg"
    driver.get(wurl)
    htmlsource = driver.page_source
    filename="%s/b.html" % tempDir
    writeFile(filename,htmlsource) 
   
    query="select w.id,w.wagelistNo,b.rawBlockName,b.fullBlockCode,b.blockCode,b.districtCode,b.stateCode,b.stateShortCode,w.finyear,b.stateName,b.districtName from wagelists w,blocks b where w.fullBlockCode=b.fullBlockCode and ( (w.isDownloaded=0) or (w.isComplete=0 and TIMESTAMPDIFF(HOUR, w.downloadAttemptDate, now()) > 48 ))  %s order by w.isDownloaded %s " % (additionalFilters,limitString)
    cur.execute(query)
    results=cur.fetchall()
    for row in results:
      [rowid,wagelistNo,blockName,fullBlockCode,blockCode,districtCode,stateCode,stateShortCode,finyear,stateName,districtName] = row
      fullfinyear=getFullFinYear(finyear)
      logger.info(" RowID : %s, wagelistNo: %s " % (str(rowid),wagelistNo)) 
      jobcardPrefix="%s-%s-" % (stateShortCode,districtCode)
      #logger.info("Jobcard Prefix : %s " % jobcardPrefix)
      fullDistrictCode=stateCode+districtCode
      if wagelistNo != '':
        #logger.info(wagelistNo)
        wurl="http://%s/netnrega/srch_wg_dtl.aspx?state_code=&district_code=%s&state_name=%s&district_name=%s&block_code=%s&wg_no=%s&short_name=%s&fin_year=%s&mode=wg" % (searchIP,fullDistrictCode,stateName.upper(),districtName.upper(),fullBlockCode,wagelistNo,stateShortCode,fullfinyear)
        logger.info("URL: %s " % wurl)
        driver.get(wurl)
        htmlsource = driver.page_source
        htmlsource=htmlsource.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
        success=0
        isComplete=0
        if ("WageList Agency Code" in htmlsource) and (jobcardPrefix in htmlsource):
          filepath=nregaRawDataDir.replace("stateName",stateName.upper()).replace("districtName",districtName.upper())
          filename=filepath+blockName.upper()+"/WAGELISTS/"+fullfinyear+"/"+wagelistNo+".html"
         # filename=filepath+blockName.upper()+"/WAGELIST/"+fullfinyear+"/"+wagelistNo+".html"
         # logger.info(filename)
          writeFile(tempDir+wagelistNo+".html",htmlsource)
          writeFile(filename,htmlsource)
          success=1
          isComplete=1
          htmlsoup=BeautifulSoup(htmlsource)
          tables=htmlsoup.findAll('table')
          for table in tables:
            #logger.info("Found the Table")
            rows=table.findAll("tr")
            for row in rows:
              cols=row.findAll("td")
              ftoNo=cols[12].text
              if ftoNo != "FTO No.":
                #logger.info("FTO No : %s " % ftoNo)
                if stateShortCode not in ftoNo:
                  isComplete=0
                else:
                  query="select * from ftos where finyear='%s' and fullBlockCode='%s' and ftoNo='%s'" % (finyear,fullBlockCode,ftoNo)
                  #logger.info(query)
                  cur.execute(query)
                  if cur.rowcount == 0:
                    query="insert into ftos (finyear,ftoNo,fullBlockCode,stateCode,districtCode,blockCode) values ('%s','%s','%s','%s','%s','%s') " % (finyear,ftoNo,fullBlockCode,stateCode,districtCode,blockCode)
                    #logger.info(query)
                    cur.execute(query)
        query="update wagelists set isDownloaded=%s,isComplete=%s,downloadAttemptDate=NOW()  where id=%s" %(str(success),str(isComplete),str(rowid))
        #logger.info(query)
        cur.execute(query)
           
   
   # driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')
   # driver.switch_to_window(maintab) 
    driverFinalize(driver)
    displayFinalize(display)

  if args["downloadFTOs"]:
    #additionalFilters=''
    #limitString= "limit 1 "
    query="select f.id,f.ftoNo,f.blockCode,f.finyear,f.fullBlockCode,b.rawBlockName,b.districtName,b.stateName,b.stateCode from ftos f,blocks b where f.fullBlockCode=b.fullBlockCode and f.isComplete=0 and   ( (f.isDownloaded=0) or (TIMESTAMPDIFF(HOUR, f.downloadAttemptDate, now()) > 48 ) or f.downloadAttemptDate is NULL )  %s order by f.downloadAttemptDate,finyear  %s " % (additionalFilters,limitString)
    logger.info(query)
    cur.execute(query)
    results=cur.fetchall()
    for row in results:
      [rowid,ftoNo,blockCode,finyear,fullBlockCode,blockName,districtName,stateName,stateCode]=row
      logger.info("districtName: %s, blockName: %s finyear: %s ftoNo: %s " % (districtName,blockName,finyear,ftoNo))
      fullfinyear=getFullFinYear(finyear)
      if ftoNo != '':
       # filepath=nregaRawDataDir.replace("stateName",stateName.upper()).replace("districtName",districtName.upper())
        filepath=nregaWebDir.replace("stateName",stateName.upper()).replace("districtName",districtName.upper())
        filename=filepath+blockName.upper()+"/FTOs/"+fullfinyear+"/"+ftoNo+".html"
        logger.info("Downloading FTO: %s " % ftoNo)
        htmlresponse,htmlsource = getFTO(fullfinyear,stateCode,ftoNo)
        logger.info("Response = %s " % htmlresponse)
        success=0
        isPopulatedString=''
        if htmlresponse['status'] == '200':
          logger.info("Status is 200")
          isPopulatedString="isPopulated=0,"
          success,outhtml=alterFTO(cur,logger,htmlsource,stateName,districtName,blockName,ftoNo,rowid)
          #htmlsource=htmlsource.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
          if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
          myfile = open(filename, "wb")
          myfile.write(outhtml.encode("UTF-8"))
          logger.info(filename)
          #writeFile(filename,htmlsource)
          #writeFile3("/home/libtech/webroot/nreganic.libtech.info/temp/"+ftoNo+".html",htmlsource)
        query="update ftos set isDownloaded=%s,%sdownloadAttemptDate=NOW()  where id=%s" %(str(success),str(isPopulatedString),str(rowid))
        logger.info(query)
        cur.execute(query)
   




  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)

if __name__ == '__main__':
  main()
