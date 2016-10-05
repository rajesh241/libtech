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
  parser.add_argument('-u', '--stateURL', help='Please enter the url of the state  page from the nrega site that you want to crawl', required=True)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  #This is a Kludge to remove all the input tags from the html because for some reason Beautiful Soup does not parse the html correctly
  regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)


  stateURL=args['stateURL']+"&"
  logger.info(stateURL) 
  r=re.findall('state_code=(.*?)\&',stateURL)
  stateCode=r[0]
  r=re.findall('state_name=(.*?)\&',stateURL)
  stateName=r[0]
  logger.info(stateCode+stateName)

  db = dbInitialize(db=stateName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  r=requests.get(stateURL)
  myhtml=r.text
  htmlsoup=BeautifulSoup(myhtml)
  table=htmlsoup.find('table',id="gvdist")
  rows = table.findAll('tr')
  for row in rows:
    columns=row.findAll('td')
    for column in columns:
      r=re.findall('district_code=(.*?)\"',str(column))
      districtCode=r[0][2:4]
      r=re.findall('district_name=(.*?)\&',str(column))
      districtName=r[0]
      logger.info("district Code: %s districtName : %s" % (districtCode,districtName))
      query="insert into districts (name,stateName,stateCode,districtCode) values ('%s','%s','%s','%s') " % (districtName,stateName,stateCode,districtCode)
      logger.info(query)
      cur.execute(query) 
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)



if __name__ == '__main__':
  main()
