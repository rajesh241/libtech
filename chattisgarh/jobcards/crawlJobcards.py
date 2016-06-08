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
from libtechFunctions import singleRowQuery
from globalSettings import datadir,nregaDataDir
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Crawl Jobcard Register')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  db = dbInitialize(db="surguja", charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  display = displayInitialize(args['visible'])
  driver = driverInitialize(args['browser'])
  
  #Start Program here
  url="http://nrega.nic.in/netnrega/sthome.aspx"
  driver.get(url)
  elem = driver.find_element_by_link_text("CHHATTISGARH")
  elem.send_keys(Keys.RETURN)
  time.sleep(1)
  elem = driver.find_element_by_link_text("SURGUJA")
  elem.send_keys(Keys.RETURN)
  time.sleep(1)
  #Query to get all the blocks
  query="select stateCode,districtCode,blockCode,name from blocks where isRequired=1"
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    stateCode=row[0]
    districtCode=row[1]
    blockCode=row[2]
    blockName=row[3]
    logger.info("Block Name" + blockName)
    elem = driver.find_element_by_link_text(blockName)
    elem.send_keys(Keys.RETURN)
    time.sleep(1)
  
    query="select name,panchayatCode,id from panchayats where isRequired=1  and stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' order by jobcardCrawlDate"
    cur.execute(query)
    panchresults = cur.fetchall()
    for panchrow in panchresults:
      panchayatName=panchrow[0]
      panchayatCode=panchrow[1]
      panchID=panchrow[2]
      logger.info(stateCode+districtCode+blockCode+blockName+panchayatCode+panchayatName)
      elem = driver.find_element_by_link_text(panchayatName)
      elem.send_keys(Keys.RETURN)
      time.sleep(1)
      elem = driver.find_element_by_link_text("Job card/Employment Register")
      elem.send_keys(Keys.RETURN)
      time.sleep(5)
      curtime = time.strftime('%Y-%m-%d %H:%M:%S')
      html_source = driver.page_source
      htmlsoup=BeautifulSoup(html_source)
     #logger.info(html_source)
     #f=open("/tmp/ab.html","w")
     #f.write(html_source)
      try:
        table=htmlsoup.find('table',align="center")
        rows = table.findAll('tr')
        status=1
      except:
        status=0
      query="update panchayats set jobcardCrawlStatus="+str(status)+", jobcardCrawlDate='"+curtime+"' where id="+str(panchID) 
      logger.info(query)
      cur.execute(query)
      logger.info("Status is " + str(status))
      if status==1:
        for tr in rows:
          cols = tr.findAll('td')
          jclink=''
          for link in tr.find_all('a'):
            jclink=link.get('href')
          if len(cols) > 2:
            jcno="".join(cols[1].text.split())
          if "CH-05" in jcno:
            logger.info(jcno)
            query="insert into jobcardRegister (jobcard,stateCode,districtCode,blockCode,panchayatCode) values ('"+jcno+"','"+stateCode+"','"+districtCode+"','"+blockCode+"','"+panchayatCode+"')"
            try:
              cur.execute(query)
            except MySQLdb.IntegrityError,e:
              errormessage=(time.strftime("%d/%m/%Y %H:%M:%S "))+str(e)+"\n"
              #errorfile.write(errormessage)
            continue
      driver.back()
      driver.back()
      time.sleep(5)
  
    driver.back()
    time.sleep(5)

# url="http://www.google.com"
# driver.get(url)
# myhtml=driver.page_source
# print myhtml
  # End program here

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
#from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
##Error File Defination
#errorfile = open('/home/goli/libtech/logs/crawlJobcards.log', 'w')
##Connect to MySQL Database
#db = MySQLdb.connect(host="localhost", user="root", passwd="golani123", db="surguja")
#cur=db.cursor()
#db.autocommit(True)
#
#driver = webdriver.Firefox()
#url="http://nrega.nic.in/netnrega/sthome.aspx"
#print url
#driver.get(url)
#elem = driver.find_element_by_link_text("CHHATTISGARH")
#elem.send_keys(Keys.RETURN)
#time.sleep(1)
#elem = driver.find_element_by_link_text("SURGUJA")
#elem.send_keys(Keys.RETURN)
#time.sleep(1)
#
##Query to get all the blocks
#query="select stateCode,districtCode,blockCode,name from blocks"
#cur.execute(query)
#results = cur.fetchall()
#for row in results:
#  stateCode=row[0]
#  districtCode=row[1]
#  blockCode=row[2]
#  blockName=row[3]
#  elem = driver.find_element_by_link_text(blockName)
#  elem.send_keys(Keys.RETURN)
#  time.sleep(1)
#
#  query="select name,panchayatCode,id from panchayats where jobcardCrawlStatus=0 and stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' "
#  cur.execute(query)
#  panchresults = cur.fetchall()
#  for panchrow in panchresults:
#    panchayatName=panchrow[0]
#    panchayatCode=panchrow[1]
#    panchID=panchrow[2]
#    print stateCode+districtCode+blockCode+blockName+panchayatCode+panchayatName
#    elem = driver.find_element_by_link_text(panchayatName)
#    elem.send_keys(Keys.RETURN)
#    time.sleep(1)
#    elem = driver.find_element_by_link_text("Job card/Employment Register")
#    elem.send_keys(Keys.RETURN)
#    time.sleep(5)
#    curtime = time.strftime('%Y-%m-%d %H:%M:%S')
#    html_source = driver.page_source
#    htmlsoup=BeautifulSoup(html_source)
#    try:
#      table=htmlsoup.find('table',align="center")
#      rows = table.findAll('tr')
#      status=1
#    except:
#      status=0
#    query="update panchayats set jobcardCrawlStatus="+str(status)+", jobcardCrawlDate='"+curtime+"' where id="+str(panchID) 
#    print query
#    cur.execute(query)
#    if status==1:
#      for tr in rows:
#        cols = tr.findAll('td')
#        jclink=''
#        for link in tr.find_all('a'):
#          jclink=link.get('href')
#        if len(cols) > 2:
#          jcno="".join(cols[1].text.split())
#        if "CH-05" in jcno:
#          print jcno
#          query="insert into jobcardRegister (jobcard,stateCode,districtCode,blockCode,panchayatCode) values ('"+jcno+"','"+stateCode+"','"+districtCode+"','"+blockCode+"','"+panchayatCode+"')"
#          try:
#            cur.execute(query)
#          except MySQLdb.IntegrityError,e:
#            errormessage=(time.strftime("%d/%m/%Y %H:%M:%S "))+str(e)+"\n"
#            errorfile.write(errormessage)
#          continue
#    driver.back()
#    driver.back()
#    time.sleep(5)
#
#  driver.back()
#  time.sleep(5)
#driver.close()
