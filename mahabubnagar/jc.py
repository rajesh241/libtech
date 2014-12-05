#! /usr/bin/env python

#This code will get the Oabcgatat Banes
import csv
from bs4 import BeautifulSoup
import requests

import MySQLdb
import time
import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


#######################
# Global Declarations
#######################

isVirtualDisplay = True;
delay = 2
url="http://www.nrega.telangana.gov.in/"
browser="Firefox"


# Error File Defination
# errorfile = open('./logs/'+__name__+'.log', 'w')


#############
# Functions
#############

def dbInitialize():
  '''
  Connect to MySQL Database
  '''
  db = MySQLdb.connect(host="localhost", user="root", passwd="root123", db="mahabubnagar")
  cur=db.cursor()
  db.autocommit(True)
  return db;

def dbFinalize(db):
  db.close()

def displayInitialize(isVirtualDisplay=True):
  if isVirtualDisplay:
    from pyvirtualdisplay import Display

    display = Display(visible=1, size=(800, 600))
    display.start()
    return display

def displayFinalize(display, isVirtualDisplay=True):
  if isVirtualDisplay:
    display.stop()

def driverInitialize(browser="Firefox"):
  if browser == "Firefox":
    profile = webdriver.FirefoxProfile()
    profile.native_events_enabled = False
    driver = webdriver.Firefox(profile)
  elif browser == "PhantomJS":
    driver = webdriver.PhantomJS()
    driver.set_window_size(1120, 550)
  else:
    driver = webdriver.Chrome()
  return driver

def driverFinalize(driver):
  driver.close()

def main():

  import argparse
  print "entered"

  parser = argparse.ArgumentParser(description='Jobcard script for crawling, download & parsing')
  parser.add_argument('-c', '--crawl', help='Crawl the jobcards numbers and populate database', required=False, action='store_const', const=True)
  parser.add_argument('-d', '--download', help='Download the jobcards & musters for each jobcard ID', required=False, action='store_const', const=True)
  parser.add_argument('-p', '--parse', help='Parse the jobcards & musters downloaded', required=False, action='store_const', const=True)
  parser.add_argument('-d', '--display', help='Display the browser', required=False, action='store_const', const=True)
  parser.add_argument('-l', '--log-file', help='Log to the specified file', required=False)

  args = vars(parser.parse_args())
  print args
  print args['crawl']

  db = dbInitialize()
  display = displayInitialize(isVirtualDisplay)
  driver = driverInitialize(browser)

  driver.get("http://www.google.com")
  print driver.page_source.encode('utf-8')

  driverFinalize(driver)
  displayFinalize(display, isVirtualDisplay)
  dbFinalize(db)

  exit(0)

if __name__ == '__main__':
  main()

def crawlJobcards(driver):
    
  driver.get(url)

  elem = driver.find_element_by_link_text("Wage Seekers")
  elem.send_keys(Keys.RETURN)
  time.sleep(1)

  elem = driver.find_element_by_link_text("Job Card Holders Information")
  elem.send_keys(Keys.RETURN)
  time.sleep(1)

  elem = driver.find_element_by_name("District")
  elem.send_keys("Mahabubnagar")
  elem.send_keys(Keys.RETURN)
  #elem.click()
  time.sleep(delay)

  elem = driver.find_element_by_name("Mandal")
  elem.send_keys("Ghattu")
  elem.send_keys(Keys.RETURN)
  #elem.click()
  time.sleep(delay)

  # Query to get all the blocks
  query="select stateCode,districtCode,blockCode,name from blocks"
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    stateCode=row[0]
    districtCode=row[1]
    blockCode=row[2]
    blockName=row[3]

  query="select name,panchayatCode,id from panchayats where jobcardCrawlStatus=0 and stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' "
  cur.execute(query)
  panchresults = cur.fetchall()
  #print panchresults

  for panchrow in panchresults:
    panchayatName=panchrow[0]
    panchayatCode=panchrow[1]
    panchID=panchrow[2]
    #print stateCode+districtCode+blockCode+blockName+panchayatCode+panchayatName
    elem = driver.find_element_by_name("Panchayat")
    elem.send_keys(panchayatName)
    elem.send_keys(Keys.RETURN)
    #elem.click()
    time.sleep(delay)

    elem = driver.find_element_by_name("Go")
    elem.send_keys(Keys.RETURN)
    
    curtime = time.strftime('%Y-%m-%d %H:%M:%S')
    html_source = driver.page_source
    htmlsoup=BeautifulSoup(html_source)
    try:
      table=htmlsoup.find('table',id="sortable")
      rows = table.findAll('tr')
      td = table.find('td')
      #print "DATA[", td.text, "]"
     # #print rows
      status=1
    except:
      status=0
    query="update panchayats set jobcardCrawlStatus="+str(status)+", jobcardCrawlDate='"+curtime+"' where id="+str(panchID) 
    # #print query
    cur.execute(query)
    if status==1:
      for tr in rows:
        td = tr.findNext('td')
        #print "DATA1[", td.text, "]"
        td = td.findNext('td')
        #print "DATA2[", td.text, "]"
        jcno = td.text.strip()
        #print "jcno", jcno
        td = td.findNext('td')
        #print "DATA3[", td.text, "]"
        gjcno = td.text.strip()
        #print "gjcno", gjcno
        td = td.findNext('td')
        #print "DATA4[", td.text, "]"
        hof = td.text
        #print "HOF", hof
        td = td.findNext('td')
        regDate = td.text
        #print "Reg Date", regDate
        issueDate = "STR_TO_DATE('"+regDate+"','"+"%d/%m/%Y')"
        td = td.findNext('td')
        caste = td.text
        #print "caste", caste
                        
        if True:
          #print jcno
          query="insert into jobcardRegister (jobcard,govtJobcard,stateCode,headOfFamily,issueDate,caste,districtCode,blockCode,panchayatCode) values ('"+jcno+"','"+gjcno+"','"+stateCode+"','"+hof+"',"+issueDate+",'"+caste+"','"+districtCode+"','"+blockCode+"','"+panchayatCode+"')"
          #print "<<", query, ">>"
          try:
            cur.execute(query)
          except MySQLdb.IntegrityError,e:
            errormessage=(time.strftime("%d/%m/%Y %H:%M:%S "))+str(e)+"\n"
            errorfile.write(errormessage)
          continue

        #exit(0)

#driver.back()
#    driver.back()
    time.sleep(delay)

#  driver.back()
  time.sleep(delay)

