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
ftofilepath="/home/goli/libtech/data/CHATTISGARH/"+districtName+"/"
query="select b.name,f.ftoNo,f.stateCode,f.districtCode,f.blockCode,f.finyear,f.id from ftoDetails f,blocks b where f.isDownloaded=0 and f.blockCode=b.blockCode and f.stateCode=b.stateCode and f.districtCode=b.districtCode ;"
cur.execute(query)
results = cur.fetchall()
for row in results:
  blockName=row[0]
  ftono=row[1]
  stateCode=row[2]
  districtCode=row[3]
  blockCode=row[4]
  finyear=row[5]
  ftoid=row[6]
  fullBlockCode=stateCode+districtCode+blockCode
  fullDistrictCode=stateCode+districtCode
  print stateCode+districtCode+blockCode+blockName
  if finyear=='15':
    fullfinyear='2014-2015'
  else:
    fullfinyear='2013-2014'
  url="http://164.100.112.66/netnrega/FTO/fto_trasction_dtl.aspx?page=p&rptblk=t&state_code=33&state_name=CHHATTISGARH&district_code="+fullDistrictCode+"&district_name="+districtName+"&block_code="+fullBlockCode+"&block_name="+blockName+"&flg=W&fin_year="+fullfinyear+"&fto_no="+ftono
  print str(ftoid)+"   "+fullfinyear+"  "+ftono
  ftofilename=ftofilepath+blockName+"/FTO/"+fullfinyear+"/"+ftono+".html"
  if not os.path.exists(os.path.dirname(ftofilename)):
    os.makedirs(os.path.dirname(ftofilename))
  r=requests.get(url)
  f = open(ftofilename, 'w')
  f.write(r.text)
  query="update ftoDetails set isDownloaded=1 where id="+str(ftoid)
  cur.execute(query)

##Query to get all the blocks
#query="select stateCode,districtCode,blockCode,name from blocks"
#cur.execute(query)
#results = cur.fetchall()
#for row in results:
#  stateCode=row[0]
#  districtCode=row[1]
#  blockCode=row[2]
#  blockName=row[3]
#  fullBlockCode=stateCode+districtCode+blockCode
#  print stateCode+districtCode+blockCode+blockName
#  url="http://164.100.112.66/netnrega/FTO/fto_reprt_detail.aspx?lflag=local&flg=W&page=b&state_name=CHHATTISGARH&state_code=33&district_name="+districtName+"&district_code="+stateCode+districtCode+"&block_name="+blockName+"&block_code="+stateCode+districtCode+blockCode+"&fin_year="+finyear+"&typ=pb&mode=b"
#  print url
#  r  = requests.get(url)
#  htmlsource=r.text
#  htmlsoup=BeautifulSoup(htmlsource)
#  for fto in htmlsoup.find_all('a'):
#    ftoNo=fto.contents[0]
#    ftoURL="http://164.100.112.66/netnrega/FTO/"+fto.get('href')
#    if fullBlockCode in ftoNo:
#      #print ftoNo
#      query="select * from ftoDetails where isdownloaded=1 and ftoNo='"+ftoNo+"';" 
#      cur.execute(query)
#      if not cur.rowcount:
#        ftofilename=ftofilepath+blockName+"/FTO/"+finyear+"/"+ftoNo+".html"
#        if not os.path.exists(os.path.dirname(ftofilename)):
#          os.makedirs(os.path.dirname(ftofilename))
#        r=requests.get(ftoURL)
#        f = open(ftofilename, 'w')
#        f.write(r.text)
#        query="insert into ftoDetails (ftoNo,stateCode,districtCode,blockCode,finyear,isdownloaded) values ('"+ftoNo+"','"+stateCode+"','"+districtCode+"','"+blockCode+"','"+finyeardb+"',1);"
#        print ftoNo+" seems to be a new fto"
#        #print query
#        cur.execute(query)
