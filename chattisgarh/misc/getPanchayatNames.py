#This code will get the Oabcgatat Banes
import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import re
import os
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
from settings import dbhost,dbuser,dbpasswd,sid,token
#Connect to MySQL Database
#db = MySQLdb.connect(host="localhost", user="root", passwd="golani123")
db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, db="surguja",charset='utf8')
cur=db.cursor()
db.autocommit(True)

#Query to get all the blocks
query="use korea"
cur.execute(query)
query="select stateCode,districtCode,blockCode,name from blocks"
cur.execute(query)
results = cur.fetchall()
for row in results:
  stateCode=row[0]
  districtCode=row[1]
  blockCode=row[2]
  name=row[3]
  print stateCode+districtCode+blockCode+name
  url="http://164.100.112.66/netnrega/Progofficer/PoIndexFrame.aspx?flag_debited=R&lflag=local&District_Code="+stateCode+districtCode+"&district_name=SURGUJA&state_name=CHHATTISGARH&state_Code=33&finyear=2014-2015&check=1&block_name="+name+"&Block_Code="+stateCode+districtCode+blockCode
  print url
  r  = requests.get(url)
  htmlsource=r.text
  htmlsoup=BeautifulSoup(htmlsource)
  table=htmlsoup.find('table',id="ctl00_ContentPlaceHolder1_gvpanch")
  for eachPanchayat in table.findAll('a'):
    panchayat=eachPanchayat.contents[0]
    panchayatLink=eachPanchayat.get('href')
    getPanchayat=re.findall(r'(?:Panchayat_Code=)\d{10}',panchayatLink)
    panchayatFullCode=getPanchayat[0]
    panchayatCode=panchayatFullCode[len(panchayatFullCode)-3:len(panchayatFullCode)]
    print panchayat+panchayatCode
    query="insert into panchayats (stateCode,districtCode,blockCode,panchayatCode,name) values ('"+stateCode+"','"+districtCode+"','"+blockCode+"','"+panchayatCode+"','"+panchayat+"')"
    cur.execute(query)
