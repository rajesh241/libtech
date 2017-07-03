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

from nrega.models import State,District,Block,Panchayat,Muster,FPSShop,FPSStatus,FPSVillage,VillageFPSStatus
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Populate Pds SHop codes from csv File')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-c', '--crawl', help='Crawl FPSShops', required=False, action='store_const', const=1)
  parser.add_argument('-e', '--enumerate', help='Enumerate entries between FPSShops', required=False, action='store_const', const=1)

  args = vars(parser.parse_args())
  return args



def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  if args['enumerate']:
    myFPSShops=FPSShop.objects.all()
    for eachFPSShop in myFPSShops:
      startYear=2016
      now = datetime.now()
      endYear=now.year
      yearArray=list(range(startYear,endYear+1))
      for eachYear in yearArray:
        if (eachYear == now.year):
           maxMonth=now.month
        else:
           maxMonth=12
        
        eachMonth=0
        while eachMonth < maxMonth:
          eachMonth=eachMonth+1
          logger.info("%d-%d" % (eachMonth,eachYear))
          myShop=FPSStatus.objects.filter(fpsShop=eachFPSShop,fpsMonth=eachMonth,fpsYear=eachYear).first()
          if myShop is None:
            FPSStatus.objects.create(fpsShop=eachFPSShop,fpsMonth=eachMonth,fpsYear=eachYear)
            logger.info("Created object")
          myShop=FPSStatus.objects.filter(fpsShop=eachFPSShop,fpsMonth=eachMonth,fpsYear=eachYear).first()

          myVillages=FPSVillage.objects.filter(fpsShop=eachFPSShop)
          for eachVillage in myVillages:
            myVillageFPSStatus=VillageFPSStatus.objects.filter(fpsVillage=eachVillage,fpsStatus=myShop).first()
            if myVillageFPSStatus is None:
              VillageFPSStatus.objects.create(fpsVillage=eachVillage,fpsStatus=myShop)
                

  if args['crawl']:
    display = displayInitialize(args['visible'])
    driver = driverInitialize(args['browser'])
    
    #Start Program here

    base_url = "http://sfc.bihar.gov.in/"
    verificationErrors = []
    accept_next_alert = True
    driver.get("http://sfc.bihar.gov.in/login.htm")
    driver.get(base_url + "/fpshopsSummaryDetails.htm")
#    Select(driver.find_element_by_id("year")).select_by_visible_text(inyear)
#    time.sleep(10)
    
    myBlocks=Block.objects.filter(fpsRequired=True)
    myBlocks=Block.objects.filter(fpsRequired=True)
    for eachBlock in myBlocks:
      logger.info("District Name: %s Block Name: %s " % (eachBlock.name,eachBlock.district.name))
      districtCode=eachBlock.district.fpsCode
      blockCode=eachBlock.fpsCode
      Select(driver.find_element_by_id("district_id")).select_by_value(districtCode)
      time.sleep(10)

      Select(driver.find_element_by_id("block_id")).select_by_value(blockCode)
      time.sleep(10)
      fps_box = driver.find_element_by_id("fpshop_id") # if your select_box has a name.. why use xpath?..... this step could use either xpath or name, but name is sooo much easier.
      fpsOptions = [z for z in fps_box.find_elements_by_tag_name("option")] #this part is cool, because it searches the elements contained inside of select_box and then adds them to the list options if they have the tag name "options"
      for fpsElement in fpsOptions:
        fpsCode=fpsElement.get_attribute("value") #
        fpsName=fpsElement.get_attribute("text") #     
        logger.info("fpsCode: %s, fpsName: %s " % (fpsCode,fpsName))
        myFPSShop=FPSShop.objects.filter(fpsCode=fpsCode).first()
        if myFPSShop is None:
          FPSShop.objects.create(fpsCode=fpsCode,name=fpsName,block=eachBlock)

#   
    driverFinalize(driver)
    displayFinalize(display)


  
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()
