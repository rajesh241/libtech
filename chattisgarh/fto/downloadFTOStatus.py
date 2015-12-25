import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
import time
import re
import sys
from MySQLdb import OperationalError
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
from settings import dbhost,dbuser,dbpasswd,sid,token
from globalSettings import datadir
from seleniumUtils import loggerFetch,displayFinalize,displayInitialize,driverInitialize,driverFinalize,argsFetch 

def main():

  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  display = displayInitialize(args['visible'])
  driver = driverInitialize()

  outdir = args['directory']
  url = args['url']

  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, db="surguja",charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  districtName="SURGUJA"
  ftofilepath=datadir+"/CHATTISGARH/"+districtName+"/"
  url="http://services.ptcmysore.gov.in/emo/Trackfto.aspx"
  #ftofilepath="/home/libtech/libtechdata/CHATTISGARH/"+districtName+"/"
  query="select b.name,f.ftoNo,f.stateCode,f.districtCode,f.blockCode,f.finyear,f.id from ftoDetails f,blocks b where TIMESTAMPDIFF(HOUR, f.statusDownloadDate, now()) > 48  and f.isStatusDownloaded=0 and f.finyear='16' and f.blockCode=b.blockCode and f.stateCode=b.stateCode and f.districtCode=b.districtCode limit 50;"
  #query="select b.name,f.ftoNo,f.stateCode,f.districtCode,f.blockCode,f.finyear,f.id from ftoDetails f,blocks b where f.isDownloaded=0 and f.blockCode=b.blockCode and f.stateCode=b.stateCode and f.districtCode=b.districtCode and b.blockCode='003';"
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
    if finyear=='16':
      fullfinyear='2015-2016'
    elif finyear=='15':
      fullfinyear='2014-2015'
    else:
      fullfinyear='2013-2014'
    
    ftofilename=ftofilepath+blockName+"/FTO/"+fullfinyear+"/"+ftono+"_status.html"
    if not os.path.exists(os.path.dirname(ftofilename)):
      os.makedirs(os.path.dirname(ftofilename))
    
    print ftofilename
    driver.get(url)
    driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtFTO").clear()
    #driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtFTO").send_keys("CH3305003_081015FTO_142597")
    driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtFTO").send_keys(ftono)
    driver.find_element_by_id("ctl00_ContentPlaceHolder1_Button1").click()
    html_source = driver.page_source
    html_source=html_source.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
   # print html_source
    f = open(ftofilename, 'w')
    f.write(html_source.encode("UTF-8"))
    query="update ftoDetails set isStatusDownloaded=1,statusDownloadDate=now() where id="+str(ftoid)
    print query
    cur.execute(query)

if __name__ == '__main__':
  main()
