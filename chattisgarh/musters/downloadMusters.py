import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
import time
import re
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
from settings import dbhost,dbuser,dbpasswd,sid,token
from globalSettings import datadir
from seleniumUtils import loggerFetch,displayFinalize,displayInitialize,driverInitialize,driverFinalize,argsFetch 
  #Getting the block code
  #inblock=sys.argv[1]
  #print inblock
  #Connect to MySQL Database
def fetchMuster(logger, driver, log_details, dir=None, url=None):
  '''
  Fetch the html for the Muster 
  '''
  logger.info("LogDetails[%s] Directory[%s] URL[%s]" %
              (log_details, dir, url))

  if dir == None:
    dir = "/root/libtech/ghattu/nrega/html"
  districtName=log_details[0]
  blockName=log_details[1]
  panchayatName=log_details[2]
  finyear=log_details[3]
  districtCode=log_details[4]
  blockCode=log_details[5]
  panchayatCode=log_details[6]
  workCode=log_details[7]
  musterNo=log_details[8]+"~~"
  print workCode+"   "+musterNo 
  url="http://164.100.112.66/netnrega/Citizen_html/Musternew.aspx?id=2&lflag=eng&ExeL=GP&fin_year="+finyear+"&state_code=33&district_code="+districtCode+"&block_code="+blockCode+"&panchayat_code="+panchayatCode+"&State_name=CHHATTISGARH&District_name="+districtName+"&Block_name="+blockName+"&panchayat_name="+panchayatName
  print url
  if url == None:
    url="http://164.100.112.66/netnrega/Citizen_html/Musternew.aspx?id=2&lflag=eng&ExeL=GP&fin_year=2015-2016&state_code=33&district_code=3305&block_code=3305005&panchayat_code=3305005056&State_name=CHHATTISGARH&District_name=SURGUJA&Block_name=LUNDRA&panchayat_name=Amadi"
  jobcard_number = 0
  filename='/tmp/m5.html'
  
  if jobcard_number != "0":
    driver.get(url)
    logger.info("Fetching...[%s]" % url)

    driver.get(url)
    time.sleep(10)
    el = driver.find_element_by_id('ctl00_ContentPlaceHolder1_ddlwork')
    for option in el.find_elements_by_tag_name('option'):
      #print option.text
      if workCode in option.text: 
        option.click() # select() in earlier versions of webdriver
        break
    time.sleep(5)
    el = driver.find_element_by_id('ctl00_ContentPlaceHolder1_ddlMsrno')
    for option in el.find_elements_by_tag_name('option'):
      print option.text
      if musterNo in option.text:
        option.click()
        break
    time.sleep(5)



    html_source = driver.page_source
    logger.debug("HTML Fetched [%s]" % html_source)
  return html_source

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
  #This is a Kludge to remove all the input tags from the html because for some reason Beautiful Soup does not parse the html correctly
  regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
  
  #File Path where all the Downloaded FTOs would be placed
  districtName="SURGUJA"
  musterfilepath=datadir+"/CHATTISGARH/"+districtName+"/"
  query="select b.name,p.name,m.musterNo,m.stateCode,m.districtCode,m.blockCode,m.panchayatCode,m.finyear,m.musterType,m.workCode,m.workName,DATE_FORMAT(m.dateFrom,'%d/%m/%Y'),DATE_FORMAT(m.dateTo,'%d/%m/%Y'),m.id from musters m,blocks b, panchayats p where b.isActive=1 and m.blockCode=b.blockCode and m.blockCode=p.blockCode and m.panchayatCode=p.panchayatCode and p.isSurvey=1 and m.finyear='16' and m.isDownloaded=0 and m.musterType='10' limit 10;"
  #query="select b.name,p.name,m.musterNo,m.stateCode,m.districtCode,m.blockCode,m.panchayatCode,m.finyear,m.musterType,m.workCode,m.workName,DATE_FORMAT(m.dateFrom,'%d/%m/%Y'),DATE_FORMAT(m.dateTo,'%d/%m/%Y'),m.id from musters m,blocks b, panchayats p where m.blockCode=b.blockCode and m.blockCode=p.blockCode and m.panchayatCode=p.panchayatCode and m.isDownloaded=0 and m.musterType='10' and m.blockCode='"+inblock+"';"
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
    print "Block Name="+blockName
    print "Panchayat Name="+panchayatName
    print "work Code ="+workCode
    print "muster ID  ="+str(musterid)
    print "muster No="+musterNo
    log_details=[districtName,blockName,panchayatName,fullfinyear,stateCode+districtCode,stateCode+districtCode+blockCode,stateCode+districtCode+blockCode+panchayatCode,workCode,musterNo] 
    
    mustersource=fetchMuster(logger, driver, log_details, outdir, url)

    myhtml=mustersource.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    myhtml1=re.sub(regex,"",myhtml)
    htmlsoup=BeautifulSoup(myhtml1)
  #  table=htmlsoup.find('table',bordercolor="#458CC0")
    try:
      table=htmlsoup.find('table',id="ctl00_ContentPlaceHolder1_grdShowRecords")
      rows = table.findAll('tr')
      errorflag=0
      print "There is not ERROR here"
    except:
      errorflag=1
      print "Cannot find the table"
    if errorflag==0:
      print "error is zero"
      musterfilename=musterfilepath+blockName+"/"+panchayatName.upper()+"/MUSTERS/"+fullfinyear+"/"+musterNo+".html"
      if not os.path.exists(os.path.dirname(musterfilename)):
        os.makedirs(os.path.dirname(musterfilename))
      f = open(musterfilename, 'w')
      f.write(myhtml1.encode("UTF-8"))
      try:
        query="update musters set isDownloaded=1,downloadDate=NOW() where id="+str(musterid)
        print query
        cur.execute(query)
      except MySQLdb.IntegrityError,e:
        errormessage=(time.strftime("%d/%m/%Y %H:%M:%S "))+str(e)+"\n"
      #  errorfile.write(errormessage)
  
  driver.close()
  driverFinalize(driver)
  displayFinalize(display)

if __name__ == '__main__':
  main()
