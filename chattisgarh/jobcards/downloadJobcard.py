#This code will get the Oabcgatat Banes
import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import time
import re
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
#Error File Defination
errorfile = open('/home/goli/libtech/logs/crawlJobcards.log', 'w')
#File Path where all the Downloaded FTOs would be placed
districtName="SURGUJA"
jcfilepath="/home/goli/libtech/data/CHATTISGARH/"+districtName+"/"
#Connect to MySQL Database
db = MySQLdb.connect(host="localhost", user="root", passwd="golani123", db="surguja")
cur=db.cursor()
db.autocommit(True)

inblock=sys.argv[1]
print inblock
i=0
query="select j.stateCode,j.districtCode,j.blockCode,j.panchayatCode,p.name,b.name from jobcardRegister j, panchayats p, blocks b where j.blockCode='"+inblock+"' and j.blockCode=p.blockCode and j.panchayatCode=p.panchayatCode and j.blockCode=b.blockCode and j.isDownloaded=0 group by j.blockCode,j.panchayatCode limit 1"
print query
cur.execute(query)
if cur.rowcount:
  driver = webdriver.Firefox()
  url="http://nrega.nic.in/netnrega/sthome.aspx"
  print url
  driver.get(url)
  elem = driver.find_element_by_link_text("CHHATTISGARH")
  elem.send_keys(Keys.RETURN)
  time.sleep(1)
  elem = driver.find_element_by_link_text("SURGUJA")
  elem.send_keys(Keys.RETURN)
  time.sleep(1)

  results = cur.fetchall()
  for row in results:
    stateCode=row[0]
    districtCode=row[1]
    blockCode=row[2]
    panchayatCode=row[3]
    panchayatName=row[4]
    blockName=row[5]
    print panchayatName+blockName 
    elem = driver.find_element_by_link_text(blockName)
    elem.send_keys(Keys.RETURN)
    time.sleep(1)
    elem = driver.find_element_by_link_text(panchayatName)
    elem.send_keys(Keys.RETURN)
    time.sleep(1)
    elem = driver.find_element_by_link_text("Job card/Employment Register")
    elem.send_keys(Keys.RETURN)
    time.sleep(5)
    query="select jobcard from jobcardRegister where isDownloaded=0 and stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' and panchayatCode='"+panchayatCode+"' limit 50"
    cur.execute(query)
    jcresults = cur.fetchall()
    for jcrow in jcresults:
      jobcard=jcrow[0]
      i=i+1
      print str(i)+"  "+jobcard
      elem = driver.find_element_by_link_text(jobcard)
      elem.send_keys(Keys.RETURN)
      time.sleep(5)
      jcsource = driver.page_source
      driver.back()
      time.sleep(2)
      myhtml=jcsource.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
      jcfilename=jcfilepath+blockName+"/"+panchayatName.upper()+"/jobcardRegister/"+jobcard.replace("/","_")+".html"
      if not os.path.exists(os.path.dirname(jcfilename)):
        os.makedirs(os.path.dirname(jcfilename))
      myfile = open(jcfilename, "w")
      myfile.write(myhtml.encode("UTF-8"))
      query="update jobcardRegister set isDownloaded=1 where jobcard='"+jobcard+"'"
      cur.execute(query)
  driver.close()
