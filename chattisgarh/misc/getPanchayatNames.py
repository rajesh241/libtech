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
sys.path.insert(0, fileDir+'/../../')
#sys.path.insert(0, rootdir)
from libtechFunctions import singleRowQuery
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize


def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing musters')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-t', '--timeout', help='Time to wait before a page loads', required=False)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-u', '--url', help='Specify the url to crawl', required=False)
  parser.add_argument('-d', '--directory', help='Specify directory to download html file to', required=False)
  parser.add_argument('-q', '--query', help='Query to specify the workset, E.g ... where id=147', required=False)
  parser.add_argument('-j', '--jobcard', help='Specify the jobcard to download/push', required=False)
  parser.add_argument('-c', '--crawl', help='Crawl the Disbursement Data', required=False)
  parser.add_argument('-f', '--fetch', help='Fetch the Jobcard Details', required=False)
  parser.add_argument('-finyear', '--finyear', help='Download musters for that finyear', required=False)
  parser.add_argument('-district', '--district', help='District for which you need to Download', required=False)
  parser.add_argument('-p', '--parse', help='Parse Jobcard HTML for Muster Info', required=False, action='store_const', const=True)
  parser.add_argument('-r', '--process', help='Process downloaded HTML files for Muster Info', required=False, action='store_const', const=True)
  parser.add_argument('-P', '--push', help='Push Muster Info into the DB on the go', required=False, action='store_const', const=True)
  parser.add_argument('-J', '--jobcard-details', help='Fetch the Jobcard Details for DB jobcardDetails table', required=False, action='store_const', const=True)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  #This is a Kludge to remove all the input tags from the html because for some reason Beautiful Soup does not parse the html correctly
  regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)

  db = dbInitialize(db="libtech", charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)

  if args['district']:
    districtName=args['district']
  else:
    districtName='surguja'
 
  logger.info("DistrictName "+districtName)

#Query to get all the blocks
  query="use libtech"
  cur.execute(query)
  query="select crawlIP from crawlDistricts where name='%s'" % districtName.lower()
  crawlIP=singleRowQuery(cur,query)
  query="select state from crawlDistricts where name='%s'" % districtName.lower()
  stateName=singleRowQuery(cur,query)
  logger.info("crawlIP "+crawlIP)
  logger.info("State Name "+stateName)
  query="use %s" % districtName.lower()
  cur.execute(query)
  finyear='2015-2016'
  query="select stateCode,districtCode,blockCode,name from blocks"
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    stateCode=row[0]
    districtCode=row[1]
    blockCode=row[2]
    blockName=row[3]
#    print stateCode+districtCode+blockCode+name
    url="http://%s/netnrega/Progofficer/PoIndexFrame.aspx?flag_debited=R&lflag=local&District_Code=%s&district_name=%s&state_name=%s&state_Code=%s&finyear=%s&check=1&block_name=%s&Block_Code=%s" %(crawlIP,stateCode+districtCode,districtName.upper(),stateName.upper(),stateCode,finyear,blockName.upper(),stateCode+districtCode+blockCode)
    logger.info("URL "+url)
#    url="http://164.100.112.66/netnrega/Progofficer/PoIndexFrame.aspx?flag_debited=R&lflag=local&District_Code="+stateCode+districtCode+"&district_name=SURGUJA&state_name=CHHATTISGARH&state_Code=33&finyear=2014-2015&check=1&block_name="+name+"&Block_Code="+stateCode+districtCode+blockCode
#    print url
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

  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)



if __name__ == '__main__':
  main()
