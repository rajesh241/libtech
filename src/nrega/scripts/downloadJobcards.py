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
from libtechFunctions import singleRowQuery,writeFile
from globalSettings import nregaDir,nregaRawDir
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable
from crawlFunctions import getDistrictParams
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Crawl Jobcard Register')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-d', '--district', help='District for which you need to Download', required=True)
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-blockCode', '--blockCode', help='BlockCode for  which you need to Download', required=False)
  parser.add_argument('-limit', '--limit', help='Limit the number of panchayats to be processed', required=False)

  args = vars(parser.parse_args())
  return args

def getCategoryBPL(inhtml):
  s=inhtml.replace("\n","")
  s=s.replace(" ","")
  a=s.split('Category:</font></td><tdvalign="top"colspan="2"><b><fontsize="2">')
  b=s.split('WhetherBPLFamily:</font></td><tdvalign="top"><b><fontsize="2">')
  category=a[1].split("<")
  bpl=b[1].split("<")
  return category[0],bpl[0]

def getSpans(htmlSoup,inhtml):
  tableHTML=''
  tableHTML+=  getCenterAligned('<h3 style="color:green"> JobCard Details</h3>'  )
  classAtt='id = "GridView0" class = " table table-striped"' 
  tableHTML+='<table %s">' % classAtt
  category,bpl=getCategoryBPL(inhtml)
  headOfHousehold=getSpanLine(htmlSoup,"Head of HouseHold","lbl_house")
  fatherHusbandName=getSpanLine(htmlSoup,"Name of Father_Husband","lbl_FATH_HUS")
  issueDate=getSpanLine(htmlSoup,"Date of Registration","lbl_head")
  village=getSpanLine(htmlSoup,"Village","lbl_vill")

  tableHTML+="<tr><th> %s </th><td> %s </td></tr>" %("Head of Household",headOfHousehold)
  tableHTML+="<tr><th> %s </th><td> %s </td></tr>" %("Father Husband Name",fatherHusbandName)
  tableHTML+="<tr><th> %s </th><td> %s </td></tr>" %("Date of Registration",issueDate)
  tableHTML+="<tr><th> %s </th><td> %s </td></tr>" %("Category",category)
  tableHTML+="<tr><th> %s </th><td> %s </td></tr>" %("Village",village)
  tableHTML+="<tr><th> %s </th><td> %s </td></tr>" %("Is BPL",bpl)
  tableHTML+='</table>'
  return tableHTML

def getSpanLine(htmlSoup,title,att):
  span=htmlSoup.find('span',{"id" : att})
  return span.text
#  return "<tr><th> %s </th><td> %s </td></tr>" %(title,span.text)

def rewriteTable(htmlSoup,title,tableID):
  myhtml=''
  myhtml+=  getCenterAligned('<h3 style="color:green"> %s</h3>' %title )
  tables=htmlSoup.findAll('table',{"id" : tableID})
  for table in tables:
    myhtml+=stripTableAttributes(table,tableID)
  return myhtml
  
def stripTableAttributes(inhtml,tableID):
  tableHTML=''
  classAtt='id = "%s" class = " table table-striped"' % tableID
  tableHTML+='<table %s">' % classAtt
  rows=inhtml.findAll('tr')
  for eachRow in rows:
    thCols=eachRow.findAll('th')
    if len(thCols) > 1:
     tableHTML+='<tr>'
     for eachTD in thCols:
       tableHTML+='<th>%s</th>' % eachTD.text
     tableHTML+='</tr>'

    tdCols=eachRow.findAll('td')
    if len(tdCols) > 1:
      tableHTML+='<tr>'
      for eachTD in tdCols:
        tableHTML+='<td>%s</td>' % eachTD.text
      tableHTML+='</tr>'

  tableHTML+='</table>'
  return tableHTML


def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  districtName=args['district']
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
  display = displayInitialize(args['visible'])
  driver = driverInitialize(args['browser'])
  jobcardPrefix="%s-%s" % (stateShortCode,districtCode)
  logger.info("crawlIP "+crawlIP)
  logger.info("State Name "+stateName)
  jcReportFilePath=nregaDir.replace("districtName",districtName.lower())+districtName.upper()+"/"
  jcReportRawFilePath=nregaRawDir.replace("districtName",districtName.lower())+districtName.upper()+"/"
  #Start Program here
  url="http://nrega.nic.in/netnrega/sthome.aspx"
  driver.get(url)
  elem = driver.find_element_by_link_text(stateName)
  elem.send_keys(Keys.RETURN)
  time.sleep(1)
  elem = driver.find_element_by_link_text(districtName.upper())
  elem.send_keys(Keys.RETURN)
  time.sleep(1)
  #Query to get all the blocks
  query="select b.blockCode,b.name,p.panchayatCode,p.name from blocks b,panchayats p where b.blockCode=p.blockCode and p.isRequired=1 and jobcardCrawlDate is not NULL order by jobcardDownloadDate %s %s" % (additionalFilters,limitString)
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    blockCode=row[0]
    blockName=row[1]
    panchayatCode=row[2]
    panchayatName=row[3]
    panchayatNameOnlyLetters=re.sub(r"[^A-Za-z]+", '', panchayatName)
    elem = driver.find_element_by_link_text(blockName)
    elem.send_keys(Keys.RETURN)
    elem = driver.find_element_by_link_text(panchayatName)
    elem.send_keys(Keys.RETURN)
    elem = driver.find_element_by_link_text("Job card/Employment Register")
    elem.send_keys(Keys.RETURN)
    time.sleep(5)
    query="update panchayats set jobcardDownloadDate=now() where blockCode='%s' and panchayatCode='%s' " % (blockCode,panchayatCode)
    cur.execute(query)
    query="select jobcard from jobcardRegister where isDownloaded=0 and stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' and panchayatCode='"+panchayatCode+"' "
    cur.execute(query)
    jcresults = cur.fetchall()
    for jcrow in jcresults:
      jobcard=jcrow[0]
      logger.info("blockName %s   panchayatName: %s jobcard: %s" % (blockName,panchayatName,jobcard) )
      elem = driver.find_element_by_link_text(jobcard)
      elem.send_keys(Keys.RETURN)
      jcsource = driver.page_source
      driver.back()
      rawhtml=jcsource.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
      htmlSoup=BeautifulSoup(rawhtml,"html")
      errorFlag=1
      try:
        tables=htmlSoup.findAll('table',{"id" : "golani"})
        errorFlag=0
      except:
        errorFlag = 1
      if errorFlag == 0:
        jcfilename=jcReportRawFilePath+blockName.upper()+"/"+panchayatNameOnlyLetters.upper()+"/jobcardRegister/"+jobcard.replace("/","_")+".html"
        logger.info(jcfilename)
        logger.info(jcfilename)
        writeFile(jcfilename,rawhtml)
        query="update jobcardRegister set isDownloaded=1 where jobcard='"+jobcard+"'"
        cur.execute(query)



  driverFinalize(driver)
  displayFinalize(display)
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()

