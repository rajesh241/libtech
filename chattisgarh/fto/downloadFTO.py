import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
#Connect to MySQL Database
db = MySQLdb.connect(host="localhost", user="root", passwd="golani123", db="surguja")
cur=db.cursor()
db.autocommit(True)
#File Path where all the Downloaded FTOs would be placed
districtName="SURGUJA"
finyear="2014-2015"
finyeardb="15"
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
      #print ftoNo
      query="select * from ftoDetails where isdownloaded=1 and ftoNo='"+ftoNo+"';" 
      cur.execute(query)
      if not cur.rowcount:
        ftofilename=ftofilepath+blockName+"/FTO/"+finyear+"/"+ftoNo+".html"
        if not os.path.exists(os.path.dirname(ftofilename)):
          os.makedirs(os.path.dirname(ftofilename))
        r=requests.get(ftoURL)
        f = open(ftofilename, 'w')
        f.write(r.text)
        query="insert into ftoDetails (ftoNo,stateCode,districtCode,blockCode,finyear,isdownloaded) values ('"+ftoNo+"','"+stateCode+"','"+districtCode+"','"+blockCode+"','"+finyeardb+"',1);"
        print ftoNo+" seems to be a new fto"
        #print query
        cur.execute(query)
