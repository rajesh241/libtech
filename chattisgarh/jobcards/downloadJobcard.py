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
from globalSettings import datadir,nregaDataDir,nregaDownloadsDir,nregaRawDownloadsDir,nregaStaticReportsDir
from crawlSettings import crawlIP,stateName,stateCode,stateShortCode,districtCode
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable
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
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  display = displayInitialize(args['visible'])
  driver = driverInitialize(args['browser'])
  jobcardPrefix="%s-%s" % (stateShortCode,districtCode)
  logger.info("crawlIP "+crawlIP)
  logger.info("State Name "+stateName)
  jcReportFilePath=nregaDownloadsDir.replace("districtName",districtName.lower())+districtName.upper()+"/"
  jcReportRawFilePath=nregaRawDownloadsDir.replace("districtName",districtName.lower())+districtName.upper()+"/"
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
  query="select b.blockCode,b.name,p.panchayatCode,p.name from blocks b,panchayats p where b.blockCode=p.blockCode and p.isRequired=1 order by jobcardCrawlDate %s" % (limitString)
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    blockCode=row[0]
    blockName=row[1]
    panchayatCode=row[2]
    panchayatName=row[3]
    elem = driver.find_element_by_link_text(blockName)
    elem.send_keys(Keys.RETURN)
    elem = driver.find_element_by_link_text(panchayatName)
    elem.send_keys(Keys.RETURN)
    elem = driver.find_element_by_link_text("Job card/Employment Register")
    elem.send_keys(Keys.RETURN)
    time.sleep(5)
    query="update panchayats set jobcardCrawlDate=now() where blockCode='%s' and panchayatCode='%s' " % (blockCode,panchayatCode)
    cur.execute(query)
    query="select jobcard from jobcardRegister where isDownloaded=0 and stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' and panchayatCode='"+panchayatCode+"' limit 50"
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
      jcfilename=jcReportRawFilePath+blockName.upper()+"/"+panchayatName.upper()+"/jobcardRegister/"+jobcard.replace("/","_")+".html"
      logger.info(jcfilename)
      writeFile(jcfilename,rawhtml)

      category,isBPL=getCategoryBPL(rawhtml)
      logger.info("Category : %s " % category)
      logger.info("isBPL : %s " % isBPL)
      htmlSoup=BeautifulSoup(rawhtml,"lxml")
     
      myhtml=''
      myhtml+=getSpans(htmlSoup,rawhtml)
      myhtml+=rewriteTable(htmlSoup,"Family Details","GridView4")
      myhtml+=rewriteTable(htmlSoup,"Requested Period of Employment","GridView1")
      myhtml+=rewriteTable(htmlSoup,"Period and Work on which Employment Offered","GridView2")
      myhtml+=rewriteTable(htmlSoup,"Period and Work on which Employment Given","GridView3")
     
     
     
      myhtml=htmlWrapperLocal(title="Jobcard Details", head='<h1 aling="center">'+jobcard+'</h1>', body=myhtml)
      jcfilename=jcReportFilePath+blockName.upper()+"/"+panchayatName.upper()+"/jobcardRegister/"+jobcard.replace("/","_")+".html"
      logger.info(jcfilename)
      writeFile(jcfilename,myhtml)
      query="update jobcardRegister set isDownloaded=1 where jobcard='"+jobcard+"'"
      cur.execute(query)




#     if not os.path.exists(os.path.dirname(jcfilename)):
#       os.makedirs(os.path.dirname(jcfilename))
#     myfile = open(jcfilename, "w")
#     myfile.write(myhtml.encode("UTF-8"))
#     query="update jobcardRegister set isDownloaded=1 where jobcard='"+jobcard+"'"
#     cur.execute(query)


  driverFinalize(driver)
  displayFinalize(display)
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()








##This code will get the Oabcgatat Banes
#import csv
#from bs4 import BeautifulSoup
#import requests
#import MySQLdb
#import time
#import re
#import os
#import sys
#from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
##Error File Defination
#errorfile = open('/home/goli/libtech/logs/crawlJobcards.log', 'w')
##File Path where all the Downloaded FTOs would be placed
#districtName="SURGUJA"
#jcfilepath="/home/goli/libtech/data/CHATTISGARH/"+districtName+"/"
##Connect to MySQL Database
#db = MySQLdb.connect(host="localhost", user="root", passwd="golani123", db="surguja")
#cur=db.cursor()
#db.autocommit(True)
#
#inblock=sys.argv[1]
#print inblock
#i=0
#query="select j.stateCode,j.districtCode,j.blockCode,j.panchayatCode,p.name,b.name from jobcardRegister j, panchayats p, blocks b where j.blockCode='"+inblock+"' and j.blockCode=p.blockCode and j.panchayatCode=p.panchayatCode and j.blockCode=b.blockCode and j.isDownloaded=0 group by j.blockCode,j.panchayatCode limit 1"
#print query
#cur.execute(query)
#if cur.rowcount:
#  driver = webdriver.Firefox()
#  url="http://nrega.nic.in/netnrega/sthome.aspx"
#  print url
#  driver.get(url)
#  elem = driver.find_element_by_link_text("CHHATTISGARH")
#  elem.send_keys(Keys.RETURN)
#  time.sleep(1)
#  elem = driver.find_element_by_link_text("SURGUJA")
#  elem.send_keys(Keys.RETURN)
#  time.sleep(1)
#
#  results = cur.fetchall()
#  for row in results:
#    stateCode=row[0]
#    districtCode=row[1]
#    blockCode=row[2]
#    panchayatCode=row[3]
#    panchayatName=row[4]
#    blockName=row[5]
#    print panchayatName+blockName 
#    elem = driver.find_element_by_link_text(blockName)
#    elem.send_keys(Keys.RETURN)
#    time.sleep(1)
#    elem = driver.find_element_by_link_text(panchayatName)
#    elem.send_keys(Keys.RETURN)
#    time.sleep(1)
#    elem = driver.find_element_by_link_text("Job card/Employment Register")
#    elem.send_keys(Keys.RETURN)
#    time.sleep(5)
#    query="select jobcard from jobcardRegister where isDownloaded=0 and stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' and panchayatCode='"+panchayatCode+"' limit 50"
#    cur.execute(query)
#    jcresults = cur.fetchall()
#    for jcrow in jcresults:
#      jobcard=jcrow[0]
#      i=i+1
#      print str(i)+"  "+jobcard
#      elem = driver.find_element_by_link_text(jobcard)
#      elem.send_keys(Keys.RETURN)
#      time.sleep(5)
#      jcsource = driver.page_source
#      driver.back()
#      time.sleep(2)
#      myhtml=jcsource.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
#      jcfilename=jcfilepath+blockName+"/"+panchayatName.upper()+"/jobcardRegister/"+jobcard.replace("/","_")+".html"
#      if not os.path.exists(os.path.dirname(jcfilename)):
#        os.makedirs(os.path.dirname(jcfilename))
#      myfile = open(jcfilename, "w")
#      myfile.write(myhtml.encode("UTF-8"))
#      query="update jobcardRegister set isDownloaded=1 where jobcard='"+jobcard+"'"
#      cur.execute(query)
#  driver.close()
