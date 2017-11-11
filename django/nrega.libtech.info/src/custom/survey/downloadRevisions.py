from bs4 import BeautifulSoup
from datetime import datetime,date
import requests
import os
import sys
import re
import time
from selenium import webdriver
sys.path.insert(0, "./../scripts")
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
from customSettings import repoDir,djangoDir,djangoSettings
import json
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getFullFinYear,savePanchayatReport
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster,WorkDetail,PanchayatReport,Jobcard,LibtechTag,PaymentDetail,Worker,Applicant
from django.db.models import Count,Sum,Q

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-f', '--revisionsFile', help='Financial year for which data needs to be crawld', required=True)
  parser.add_argument('-n', '--name', help='Financial year for which data needs to be crawld', required=True)
  parser.add_argument('-gid', '--googleFileID', help='StateCode for which the numbster needs to be downloaded', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1
  filename=args['revisionsFile']
  googleID=args['googleFileID']
  name=args['name']
  dirname=name
  username="libtech.stanford"
  passwd="ccmpProject**"

#  display = displayInitialize(args['visible'])
#  driver = driverInitialize(args['browser'])
#  driver.get('http://gmail.com')
#  driver.get('https://accounts.google.com/ServiceLogin?service=mail#identifier')
# action = webdriver.ActionChains(driver)
# usernametext = driver.find_element_by_name('Email')
# usernametext.send_keys(username) #put your actual username
# driver.find_element_by_name('signIn').click()
# #Password input field identification and data entered
# passwordtext = driver.find_element_by_id(passwd)
# passwordtext.send_keys("mypassword") #put your actual password
# driver.find_element_by_id('signIn').click()


  with open(filename) as data_file:    
    revisionData = json.load(data_file)
  totalRevisions=len(revisionData["revisions"])
  
  logger.info("Total Revisions %s " % str(totalRevisions))
  s='' 
  i =0
  while i < totalRevisions:
    fileID=revisionData["revisions"][i]["id"]
    timestamp=revisionData["revisions"][i]["modifiedTime"]
    logger.info("for %s FileID: %s timeStamp: %s " % (str(i),fileID,timestamp))
    i=i+1
    downloadURL="https://docs.google.com/spreadsheets/d/%s/export?format=xlsx&revision=%s" % (googleID,fileID)
    s+=downloadURL
 #   s+='open location  "%s"' %downloadURL
    s+="\n"
  #  s+="delay 15"
  #  s+="\n"
   
    logger.info(downloadURL)
    timestamp=timestamp.split(".")[0]
    outputFile="surveyData/%s/data/%s-%s-%s.xlsx" % (dirname,name,fileID,timestamp)
    cmd="wget -O %s %s" % (outputFile,downloadURL)
    logger.info(cmd)
 #   os.system(cmd) 
 #   time.sleep(10)


  with open("/tmp/urls.txt","w") as f:
    f.write(s)
#  driverFinalize(driver)
#  displayFinalize(display)
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
