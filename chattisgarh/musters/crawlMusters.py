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
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
from settings import dbhost,dbuser,dbpasswd,sid,token
#This is a Kludge to remove all the input tags from the html because for some reason Beautiful Soup does not parse the html correctly
regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)


#Error File Defination
errorfile = open('/tmp/crawlJobcards.log', 'w')
#Connect to MySQL Database
db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
cur=db.cursor()
db.autocommit(True)
#Query to set up Database to read Hindi Characters
query="SET NAMES utf8"
cur.execute(query)
district=sys.argv[1]
finyear=sys.argv[2]
#muster Type list
musterTypeList= ['10','11','13','14']
if finyear=='16':
  fullfinyear='2015-2016'
elif finyear=='15':
  fullfinyear='2014-2015'
elif finyear=='14':
  fullfinyear='2013-2014'
else:
  fullfinyear='2013-2014'
#   Some Constants 
districtName="SURGUJA"
districtName=district
dbname=district

query="use "+dbname
print query
cur.execute(query)
#Query to get all the blocks
query="select stateCode,districtCode,blockCode,name from blocks where isActive=1"
query="select stateCode,districtCode,blockCode,name from blocks "
#query="select stateCode,districtCode,blockCode,name from blocks where blockCode='002'"
cur.execute(query)
results = cur.fetchall()
for row in results:
  stateCode=row[0]
  districtCode=row[1]
  blockCode=row[2]
  blockName=row[3]
  print blockName
  query="select name,panchayatCode,id from panchayats where isChaupal=1 and stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' "
#  query="select name,panchayatCode,id from panchayats where stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' "
  cur.execute(query)
  panchresults = cur.fetchall()
  for panchrow in panchresults:
    panchayatName=panchrow[0]
    panchayatCode=panchrow[1]
    fullPanchayatCode=stateCode+districtCode+blockCode+panchayatCode
    panchID=panchrow[2]
    print blockName+"  "+panchayatName
    #We need to now run this for each musterType
    status=1 
    for musterType in musterTypeList:
      url="http://164.100.112.66/netnrega/state_html/emuster_wage_rep1.aspx?type="+str(musterType)+"&lflag=eng&state_name=CHHATTISGARH&district_name="+districtName+"&block_name="+blockName+"&panchayat_name="+panchayatName+"&panchayat_code="+fullPanchayatCode+"&fin_year="+fullfinyear
      print url
      r  = requests.get(url)
      curtime = time.strftime('%Y-%m-%d %H:%M:%S')
      htmlsource=r.text
      htmlsource1=re.sub(regex,"",htmlsource)
      htmlsoup=BeautifulSoup(htmlsource1)
      try:
        table=htmlsoup.find('table',bordercolor="green")
        rows = table.findAll('tr')
        errorflag=0
      except:
        status=0
        errorflag=1
      if errorflag==0:
        for tr in rows:
          cols = tr.findAll('td')
          tdtext=''
          district= cols[1].string.strip()
          block= cols[2].string.strip()
          panchayat= cols[3].string.strip()
          worknameworkcode=cols[5].text
          if district!="District":
            emusterno="".join(cols[6].text.split())
            print emusterno
            datefromdateto="".join(cols[7].text.split())
            datefromstring=datefromdateto[0:datefromdateto.index("-")]
            datetostring=datefromdateto[datefromdateto.index("-") +2:len(datefromdateto)]
            if datefromstring != '':
              datefrom = time.strptime(datefromstring, '%d/%m/%Y')
              datefrom = time.strftime('%Y-%m-%d %H:%M:%S', datefrom)
            else:
              datefrom=''
            if datetostring != '':
              dateto = time.strptime(datetostring, '%d/%m/%Y')
              dateto = time.strftime('%Y-%m-%d %H:%M:%S', dateto)
            else:
              dateto=''
            worknameworkcodearray=re.match(r'(.*)\(330(.*)\)',worknameworkcode)
            workName=worknameworkcodearray.groups()[0]
            workCode='330'+worknameworkcodearray.groups()[1]
            print emusterno+" "+datefromstring+"  "+datetostring+"  "+workCode
            query="insert into musters (musterNo,stateCode,districtCode,blockCode,panchayatCode,musterType,finyear,workCode,workName,dateFrom,dateTo,crawlDate) values ('"+emusterno+"','"+stateCode+"','"+districtCode+"','"+blockCode+"','"+panchayatCode+"','"+musterType+"','"+finyear+"','"+workCode+"','"+workName+"','"+datefrom+"','"+dateto+"',NOW())"
            try:
              cur.execute(query)
            except MySQLdb.IntegrityError,e:
              errormessage=(time.strftime("%d/%m/%Y %H:%M:%S "))+str(e)+"\n"
              errorfile.write(errormessage)
              continue
             
