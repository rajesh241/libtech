import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
import time
#Error File Defination
errorfile = open('/tmp/crawlfto.log', 'w')
#Connect to MySQL Database
db = MySQLdb.connect(host="localhost", user="root", passwd="ccmpProject**", db="surguja")
cur=db.cursor()
db.autocommit(True)
#File Path where all the Downloaded FTOs would be placed
districtName="SURGUJA"
finyear="2015-2016"
finyeardb="16"
ftofilepath="/home/goli/libtech/data/CHATTISGARH/"+districtName+"/"
#Query to get all the blocks
query="select stateCode,districtCode,blockCode,name from blocks"
cur.execute(query)
results = cur.fetchall()
for row in results:
  stateCode=row[0]
  districtCode=row[1]
  blockCode=row[2]
  blockName=row[3]
  fullBlockCode=stateCode+districtCode+blockCode
  print stateCode+districtCode+blockCode+blockName
  url="http://164.100.112.66/netnrega/FTO/fto_reprt_detail.aspx?lflag=local&flg=W&page=b&state_name=CHHATTISGARH&state_code=33&district_name="+districtName+"&district_code="+stateCode+districtCode+"&block_name="+blockName+"&block_code="+stateCode+districtCode+blockCode+"&fin_year="+finyear+"&typ=pb&mode=b"
  print url
  r  = requests.get(url)
  htmlsource=r.text
  htmlsoup=BeautifulSoup(htmlsource)
  for fto in htmlsoup.find_all('a'):
    ftoNo=fto.contents[0]
    ftoURL="http://164.100.112.66/netnrega/FTO/"+fto.get('href')
    if fullBlockCode in ftoNo:
      query="insert into ftoDetails (ftoNo,stateCode,districtCode,blockCode,finyear) values ('"+ftoNo+"','"+stateCode+"','"+districtCode+"','"+blockCode+"','"+finyeardb+"');"
      try:
        cur.execute(query)
      except MySQLdb.IntegrityError,e:
        errormessage=(time.strftime("%d/%m/%Y %H:%M:%S "))+str(e)+"\n"
        errorfile.write(errormessage)
      continue
