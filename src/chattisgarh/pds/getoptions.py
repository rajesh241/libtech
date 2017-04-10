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
query="select blockCode,name,pdsBlockCode from blocks"
cur.execute(query)
results = cur.fetchall()
for row in results:
  blockCode=row[0]
  name=row[1]
  block=row[2]
  print blockCode+name
  driver = webdriver.Firefox()
  url="http://khadya.cg.nic.in/pdsonline/cgfsa/Report/FrmRation_Patra_Allot_VerificationDistWise_Aug14.aspx"
  print url
  driver.get(url)
  time.sleep(2)
  driver.find_element_by_xpath("//select[@id='drpdist']/option[@value='39']").click()
  driver.find_element_by_xpath("//select[@id='ddlUrban_Rural']/option[@value='R']").click()
  time.sleep(2)
  driver.find_element_by_xpath("//select[@id='ddlNNN_Block']/option[@value='"+block+"']").click()
  time.sleep(2)
  select_box = driver.find_element_by_name("ddlShopName") # if your select_box has a name.. why use xpath?..... this step could use either xpath or name, but name is sooo much easier.
  options = [x for x in select_box.find_elements_by_tag_name("option")] #this part is cool, because it searches the elements contained inside of select_box and then adds them to the list options if they have the tag name "options"
  for element in options:
    shopCode=element.get_attribute("value") #
    query="insert into pdsShops (blockCode,shopCode) values ('"+blockCode+"','"+shopCode+"')";
    cur.execute(query)
    print query
  driver.close()
