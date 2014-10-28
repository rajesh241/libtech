#This code will get the Oabcgatat Banes
import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
#Error File Defination
errorfile = open('/home/goli/libtech/logs/crawlJobcards.log', 'w')
#Connect to MySQL Database
db = MySQLdb.connect(host="localhost", user="root", passwd="golani123", db="surguja")
cur=db.cursor()
db.autocommit(True)

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

#Query to get all the blocks
query="select stateCode,districtCode,blockCode,name from blocks"
cur.execute(query)
results = cur.fetchall()
for row in results:
  stateCode=row[0]
  districtCode=row[1]
  blockCode=row[2]
  blockName=row[3]
  elem = driver.find_element_by_link_text(blockName)
  elem.send_keys(Keys.RETURN)
  time.sleep(1)

  query="select name,panchayatCode,id from panchayats where jobcardCrawlStatus=0 and stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' "
  cur.execute(query)
  panchresults = cur.fetchall()
  for panchrow in panchresults:
    panchayatName=panchrow[0]
    panchayatCode=panchrow[1]
    panchID=panchrow[2]
    print stateCode+districtCode+blockCode+blockName+panchayatCode+panchayatName
    elem = driver.find_element_by_link_text(panchayatName)
    elem.send_keys(Keys.RETURN)
    time.sleep(1)
    elem = driver.find_element_by_link_text("Job card/Employment Register")
    elem.send_keys(Keys.RETURN)
    time.sleep(5)
    curtime = time.strftime('%Y-%m-%d %H:%M:%S')
    html_source = driver.page_source
    htmlsoup=BeautifulSoup(html_source)
    try:
      table=htmlsoup.find('table',align="center")
      rows = table.findAll('tr')
      status=1
    except:
      status=0
    query="update panchayats set jobcardCrawlStatus="+str(status)+", jobcardCrawlDate='"+curtime+"' where id="+str(panchID) 
    print query
    cur.execute(query)
    if status==1:
      for tr in rows:
        cols = tr.findAll('td')
        jclink=''
        for link in tr.find_all('a'):
          jclink=link.get('href')
        if len(cols) > 2:
          jcno="".join(cols[1].text.split())
        if "CH-05" in jcno:
          print jcno
          query="insert into jobcardRegister (jobcard,stateCode,districtCode,blockCode,panchayatCode) values ('"+jcno+"','"+stateCode+"','"+districtCode+"','"+blockCode+"','"+panchayatCode+"')"
          try:
            cur.execute(query)
          except MySQLdb.IntegrityError,e:
            errormessage=(time.strftime("%d/%m/%Y %H:%M:%S "))+str(e)+"\n"
            errorfile.write(errormessage)
          continue
    driver.back()
    driver.back()
    time.sleep(5)

  driver.back()
  time.sleep(5)
driver.close()
