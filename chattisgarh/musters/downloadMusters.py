import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
import time
import re
import sys
#Getting the block code
inblock=sys.argv[1]
print inblock
#Connect to MySQL Database
db = MySQLdb.connect(host="localhost", user="root", passwd="ccmpProject**", db="surguja",charset='utf8')
cur=db.cursor()
db.autocommit(True)
#Query to set up Database to read Hindi Characters
query="SET NAMES utf8"
cur.execute(query)
#This is a Kludge to remove all the input tags from the html because for some reason Beautiful Soup does not parse the html correctly
regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)

#File Path where all the Downloaded FTOs would be placed
districtName="SURGUJA"
musterfilepath="/home/libtech/data/CHATTISGARH/"+districtName+"/"
query="select b.name,p.name,m.musterNo,m.stateCode,m.districtCode,m.blockCode,m.panchayatCode,m.finyear,m.musterType,m.workCode,m.workName,DATE_FORMAT(m.dateFrom,'%d/%m/%Y'),DATE_FORMAT(m.dateTo,'%d/%m/%Y'),m.id from musters m,blocks b, panchayats p where m.blockCode=b.blockCode and m.blockCode=p.blockCode and m.panchayatCode=p.panchayatCode and m.isDownloaded=0 ;"
query="select b.name,p.name,m.musterNo,m.stateCode,m.districtCode,m.blockCode,m.panchayatCode,m.finyear,m.musterType,m.workCode,m.workName,DATE_FORMAT(m.dateFrom,'%d/%m/%Y'),DATE_FORMAT(m.dateTo,'%d/%m/%Y'),m.id from musters m,blocks b, panchayats p where m.blockCode=b.blockCode and m.blockCode=p.blockCode and m.panchayatCode=p.panchayatCode and m.isDownloaded=0 and m.musterType='10' and m.blockCode='"+inblock+"';"
print query
cur.execute(query)
results = cur.fetchall()
for row in results:
  blockName=row[0]
  panchayatName=row[1]
  musterNo=row[2]
  stateCode=row[3]
  districtCode=row[4]
  blockCode=row[5]
  panchayatCode=row[6]
  finyear=row[7]
  musterType=row[8]
  workCode=row[9]
  workName=row[10].decode("UTF-8")
  dateTo=row[11]
  dateFrom=row[12]
  musterid=row[13]
  fullPanchayatCode=stateCode+districtCode+blockCode+panchayatCode
  fullBlockCode=stateCode+districtCode+blockCode
  fullDistrictCode=stateCode+districtCode
  worknameplus=workName.replace(" ","+")
  datetostring = str(dateTo)
  datefromstring = str(dateFrom)
 
  #print stateCode+districtCode+blockCode+blockName
  if finyear=='16':
    fullfinyear='2015-2016'
  elif finyear=='15':
    fullfinyear='2014-2015'
  else:
    fullfinyear='2013-2014'
  musterurl="http://164.100.112.66/netnrega/citizen_html/musternew.aspx?lflag=eng&id=1&state_name=CHHATTISGARH&district_name="+districtName+"&block_name="+blockName+"&panchayat_name="+panchayatName+"&block_code="+fullBlockCode+"&msrno="+musterNo+"&finyear="+fullfinyear+"&workcode="+workCode+"&dtfrm="+datefromstring+"&dtto="+datetostring+"&wn="+worknameplus
  #print workName+"  "+workCode
  print musterurl
  print str(musterid)+"  "+str(musterNo)+"  "+blockName+"  "+panchayatName
  r=requests.get(musterurl)
  mustersource=r.text
  myhtml=mustersource.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
  myhtml1=re.sub(regex,"",myhtml)
  htmlsoup=BeautifulSoup(myhtml1)
  table=htmlsoup.find('table',bordercolor="#458CC0")
  try:
    table=htmlsoup.find('table',bordercolor="#458CC0")
    rows = table.findAll('tr')
    errorflag=0
  except:
    errorflag=1
  if errorflag==0:
    print "error is zero"
    musterfilename=musterfilepath+blockName+"/"+panchayatName.upper()+"/MUSTERS/"+fullfinyear+"/"+musterNo+".html"
    if not os.path.exists(os.path.dirname(musterfilename)):
      os.makedirs(os.path.dirname(musterfilename))
    f = open(musterfilename, 'w')
    f.write(myhtml1.encode("UTF-8"))
    query="update musters set isDownloaded=1 where id="+str(musterid)
    print query
    cur.execute(query)
