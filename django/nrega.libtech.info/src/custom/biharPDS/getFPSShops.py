from bs4 import BeautifulSoup
from queue import Queue
from threading import Thread
import threading
from datetime import datetime,date,timedelta
import requests
import os
import sys
import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
sys.path.insert(0, "./../scripts")
from customSettings import repoDir,djangoDir,djangoSettings
from customSettings import musterTimeThreshold
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getFullFinYear
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.db.models import Q
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Populate Pds SHop codes from csv File')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-y', '--year', help='Year for which PDS needs to be downloaded', required=True)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)

  args = vars(parser.parse_args())
  return args



def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  inyear=args['year']
  
  logger.info(inyear)
  display = displayInitialize(args['visible'])
  driver = driverInitialize(args['browser'])
  
  #Start Program here

  base_url = "http://sfc.bihar.gov.in/"
  verificationErrors = []
  accept_next_alert = True
  driver.get("http://sfc.bihar.gov.in/login.htm")
  driver.get(base_url + "/fpshopsSummaryDetails.htm")
  Select(driver.find_element_by_id("year")).select_by_visible_text(inyear)
  time.sleep(10)
  select_box = driver.find_element_by_id("district_id") # if your select_box has a name.. why use xpath?..... this step could use either xpath or name, but name is sooo much easier.
  options = [x for x in select_box.find_elements_by_tag_name("option")] #this part is cool, because it searches the elements contained inside of select_box and then adds them to the list options if they have the tag name "options"
  for element in options:
    districtCode=element.get_attribute("value") #
    districtName=element.get_attribute("text") #
    logger.info("District code; %s  District Name: %s " % (districtCode,districtName))
#   myDistrict=District.objects.filter(name=districtName,state__code='05').first()
#   nregaCode=None
#   if myDistrict is not None:
#     nregaCode=myDistrict.code
#     myDistrict.fpsCode=districtCode
#     myDistrict.save()
    #else:
    myDistrict=District.objects.filter(fpsCode=districtCode).first()
    if myDistrict is not None:
      logger.info(myDistrict.name)
    #  logger.info("District Code: %s   District Name: %s NREGA COde: %s" %(districtCode,districtName,nregaCode)) 
      
      Select(driver.find_element_by_id("district_id")).select_by_value(districtCode)
      time.sleep(10)
      block_box = driver.find_element_by_id("block_id") # if your select_box has a name.. why use xpath?..... this step could use either xpath or name, but name is sooo much easier.
      blockOptions = [y for y in block_box.find_elements_by_tag_name("option")] #this part is cool, because it searches the elements contained inside of select_box and then adds them to the list options if they have the tag name "options"
      for blockElement in blockOptions:
        blockCode=blockElement.get_attribute("value") #
        blockName=blockElement.get_attribute("text") #
        logger.info("districtCode:%s  districtName:%s  blockCode:%s  blockName:%s " % (districtCode,districtName,blockCode,blockName))
        myBlock=Block.objects.filter(district=myDistrict.id,name=blockName).first()
        if myBlock is None:
          logger.info("BlockCode not Found")
        else:
          myBlock.fpsCode=blockCode
          myBlock.save()
#     Select(driver.find_element_by_id("block_id")).select_by_value(blockCode)
#     time.sleep(10)
#     fps_box = driver.find_element_by_id("fpshop_id") # if your select_box has a name.. why use xpath?..... this step could use either xpath or name, but name is sooo much easier.
#     fpsOptions = [z for z in fps_box.find_elements_by_tag_name("option")] #this part is cool, because it searches the elements contained inside of select_box and then adds them to the list options if they have the tag name "options"
#     for fpsElement in fpsOptions:
#       fpsCode=fpsElement.get_attribute("value") #
#       fpsName=fpsElement.get_attribute("text") #
#       
#       myString=districtCode+','+districtName+','+blockCode+','+blockName+','+fpsCode+','+fpsName
#       #logger.info(myString)
#       if "Select" in myString:
#         logger.info("This will not be entered into Database")
#       else: 
#         fpsName1=cleanFPSName(fpsName)
#         whereClause="where fpsCode='%s' and blockCode='%s' and districtCode='%s' " % (fpsCode,blockCode,districtCode)
#         query="select * from fpsShops %s " % (whereClause)
#         #cur.execute(query)
#         if cur.rowcount == 0:
#           query="insert into fpsShops (fpsCode,blockCode,districtCode) values ('%s','%s','%s') " % (fpsCode,blockCode,districtCode)
#           #cur.execute(query)
#         query="update fpsShops set districtName='%s',blockName='%s',fpsName='%s' %s " % (districtName,blockName,fpsName1,whereClause)
#         logger.info(query) 
#         #cur.execute(query)



  # End program here

  driverFinalize(driver)
  displayFinalize(display)


  
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()
