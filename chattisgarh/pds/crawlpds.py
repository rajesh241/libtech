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
errorfile = open('/tmp/crawlpds.log', 'w')
#Connect to MySQL Database
db = MySQLdb.connect(host="localhost", user="root", passwd="golani123", db="surguja")
cur=db.cursor()
db.autocommit(True)

#Query to get all the blocks
query="select b.pdsBlockCode,s.shopCode,b.name from pdsShops s,blocks b where b.blockCode=s.blockCode "
cur.execute(query)
results = cur.fetchall()
for row in results:
  pdsBlockCode=row[0]
  blockName=row[2]
  shopCode=row[1]
  print blockName+shopCode 
  driver = webdriver.Firefox()
  url="http://khadya.cg.nic.in/pdsonline/cgfsa/Report/FrmRation_Patra_Allot_VerificationDistWise_Aug14.aspx"
  print url
  driver.get(url)
  time.sleep(2)
  driver.find_element_by_xpath("//select[@id='drpdist']/option[@value='39']").click()
  driver.find_element_by_xpath("//select[@id='ddlUrban_Rural']/option[@value='R']").click()
  time.sleep(2)
  driver.find_element_by_xpath("//select[@id='ddlNNN_Block']/option[@value='"+pdsBlockCode+"']").click()
  time.sleep(2)
  driver.find_element_by_xpath("//select[@id='ddlShopName']/option[@value='"+shopCode+"']").click()
  time.sleep(2)
  elem=driver.find_element_by_name("btnShowDetails")
  elem.send_keys(Keys.RETURN)
  time.sleep(2)
  jcsource = driver.page_source
  myhtml=jcsource.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
  myfile = open('./'+shopCode+'.html', "w")
  myfile.write(myhtml.encode("UTF-8"))
  myfile.close
  driver.close()
