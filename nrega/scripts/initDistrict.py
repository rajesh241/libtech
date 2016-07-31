import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import re
import os
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
from settings import dbhost,dbuser,dbpasswd
sys.path.insert(0, fileDir+'/../../')
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize


def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-u', '--districtURL', help='Please enter the URL of the district page from the nrega site that you want to crawl', required=True)
  parser.add_argument('-jp', '--jobcardPrefix', help='Enter the Jobcard Prefix for the state for example chatisgarh is CH, and Karnataka is KN', required=True)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  #This is a Kludge to remove all the input tags from the html because for some reason Beautiful Soup does not parse the html correctly
  regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)


  districtURL=args['districtURL']+"&"
  stateShortCode=args['jobcardPrefix']

  r=re.findall('http://(.*?)\/',districtURL)
  crawlIP=r[0]
  r=re.findall('district_code=(.*?)\&',districtURL)
  districtCode=r[0][2:4]
  r=re.findall('state_Code=(.*?)\&',districtURL)
  stateCode=r[0]
  r=re.findall('state_name=(.*?)\&',districtURL)
  stateName=r[0]
  r=re.findall('district_name=(.*?)\&',districtURL)
  districtName=r[0]
  logger.info("Crawl IP : %s " ,crawlIP) 
  logger.info("District Code : %s " ,districtCode) 
  logger.info("State Code : %s " ,stateCode) 
  logger.info("District Name : %s " ,districtName) 
  logger.info("State Name : %s " ,stateName)
  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  s='''
districtName='%s'
crawlIP='%s'
stateName='%s'
stateShortCode='%s'
districtCode='%s'
stateCode='%s'
  ''' % (districtName,crawlIP,stateName,stateShortCode,districtCode,stateCode)
  filename="../crawlDistricts/%s.py" % (districtName.lower())
  f = open(filename, 'w')
  f.write(s.encode("UTF-8"))
  query="insert into crawlDistricts.districts (name,crawlIP,state,stateShortCode,stateCode,districtCode) values ('%s','%s','%s','%s','%s','%s')" %(districtName.upper(),crawlIP,stateName,stateShortCode,stateCode,districtCode)
  logger.info(query)
  cur.execute(query) 
  r=re.findall('=(.*?)\&',districtURL)
  query="use %s " % districtName.lower()
  cur.execute(query)
  r=requests.get(districtURL)
  blockHTML=r.text
  htmlsoup=BeautifulSoup(blockHTML)
  table=htmlsoup.find('table',id="gvdpc")
  rows = table.findAll('tr')
  for row in rows:
    columns=row.findAll('td')
    for column in columns:
      r=re.findall('Block_Code=(.*?)\"',str(column))
      blockCode=r[0][4:8]
      r=re.findall('block_name=(.*?)\&',str(column))
      blockName=r[0]
      logger.info("Block Code: %s BlockName : %s" % (blockCode,blockName))
      query="insert into blocks (name,stateCode,districtCode,blockCode,isRequired) values ('%s','%s','%s','%s',1)" % (blockName,stateCode,districtCode,blockCode)
      logger.info(query)
      finyear='2015-2016'
      cur.execute(query)
      panchayaturl="http://%s/netnrega/Progofficer/PoIndexFrame.aspx?flag_debited=R&lflag=local&District_Code=%s&district_name=%s&state_name=%s&state_Code=%s&finyear=%s&check=1&block_name=%s&Block_Code=%s" %(crawlIP,stateCode+districtCode,districtName.upper(),stateName.upper(),stateCode,finyear,blockName.upper(),stateCode+districtCode+blockCode)
      logger.info("URL "+panchayaturl)
      r  = requests.get(panchayaturl)
      htmlsource1=r.text
      htmlsoup1=BeautifulSoup(htmlsource1)
      table1=htmlsoup1.find('table',id="ctl00_ContentPlaceHolder1_gvpanch")
      for eachPanchayat in table1.findAll('a'):
        panchayat=eachPanchayat.contents[0]
        panchayatNameOnlyLetters=re.sub(r"[^A-Za-z]+", '', panchayat)
        panchayatLink=eachPanchayat.get('href')
        getPanchayat=re.findall(r'(?:Panchayat_Code=)\d{10}',panchayatLink)
        panchayatFullCode=getPanchayat[0]
        panchayatCode=panchayatFullCode[len(panchayatFullCode)-3:len(panchayatFullCode)]
        print panchayat+panchayatCode
        query="insert into panchayats (isRequired,stateCode,districtCode,blockCode,panchayatCode,name,rawName) values (1,'"+stateCode+"','"+districtCode+"','"+blockCode+"','"+panchayatCode+"','"+panchayatNameOnlyLetters+"','"+panchayat+"')"
        logger.info(query)
        cur.execute(query)
   

  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)



if __name__ == '__main__':
  main()
