from bs4 import BeautifulSoup
from urllib.parse import urlencode
import httplib2
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

from nregaFunctions import stripTableAttributes,stripTableAttributesOrdered,htmlWrapperLocal,getFullFinYear
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.db.models import Q
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster,FPSShop,FPSStatus
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Populate Pds SHop codes from csv File')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-m', '--month', help='Month for which PDS needs to be downloaded', required=False)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-f', '--fpsCode', help='FPS shop for which data needs to be donwloaded', required=False)

  args = vars(parser.parse_args())
  return args


def main():
  httplib2.debuglevel = 1
  monthLabels=['0','JAN','FEB','MAR','APR','MAY','JUNE','JULY','AUG','SEP','OCT','NOV','DEC']
  searchText='class="newFormTheme"'
  replaceText='class="newFormTheme" id="newFormTheme"'
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  limit=100000
  logger.info("BEGIN PROCESSING...")
  if args['fpsCode']:
    incode=args['fpsCode']
    myShops=FPSStatus.objects.filter(fpsShop__fpsCode=incode,isComplete=False,isDownloaded=True)[:limit]
  else:
    myShops=FPSStatus.objects.filter(isComplete=False,isDownloaded=True).order_by('isDownloaded')[:limit]
  for eachShop in myShops:
    statusID=eachShop.id
    districtCode=eachShop.fpsShop.block.district.fpsCode
    blockCode=eachShop.fpsShop.block.fpsCode
    fpsCode=eachShop.fpsShop.fpsCode
    districtName=eachShop.fpsShop.block.district.name
    blockName=eachShop.fpsShop.block.name
    fpsName=eachShop.fpsShop.name
    fpsSlug=eachShop.fpsShop.slug
    stateName=eachShop.fpsShop.block.district.state.name
    fpsMonth=eachShop.fpsMonth
    fpsYear=eachShop.fpsYear
    fpsMonthName=monthLabels[int(fpsMonth)]   
    myhtml=eachShop.statusFile.read()
    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    myTable=htmlsoup.find('table',id="deliveryTable")
    logger.info("Processing statusID: %s, state: %s fpsCode: %s district: %s, block: %s ShopName : %s fpsMonth:%s fpsYear: %s" % (str(statusID),stateName,fpsCode,districtName,blockName,fpsName,str(fpsMonth),str(fpsYear)))
    AAYDeliveryDate=None
    PHHDeliveryDate=None
    if myTable is not None:
      logger.info("Table Found")
      rows=myTable.findAll('tr')
      for row in rows:
        logger.info('Found a row')
        cols=row.findAll('td')
        schemeName=cols[0].text.lstrip().rstrip()
        if schemeName=='AAY':
          deliveryDateColValue=cols[8].text.lstrip().rstrip().replace("\n","")
          fpsArray=deliveryDateColValue.split('Date of Delivered. : ')
          if len(fpsArray) > 1:
            AAYDeliveryDateString=fpsArray[1][0:10]
            AAYDeliveryDate=datetime.strptime(AAYDeliveryDateString, "%d-%m-%Y").date()
         #   AAYDeliveryDate = time.strptime(AAYDeliveryDateString, '%d-%m-%Y')
         #   AAYDeliveryDate = time.strftime('%Y-%m-%d', AAYDeliveryDate)
            logger.info(AAYDeliveryDate)
        if schemeName=='PHH':
          deliveryDateColValue=cols[8].text.lstrip().rstrip().replace("\n","")
          fpsArray=deliveryDateColValue.split('Date of Delivered. : ')
          if len(fpsArray) > 1:
            PHHDeliveryDateString=fpsArray[1][0:10]
            PHHDeliveryDate=datetime.strptime(PHHDeliveryDateString, "%d-%m-%Y").date()
            logger.info(PHHDeliveryDate)
    if (PHHDeliveryDate is not None) and (AAYDeliveryDate is not None):
      eachShop.isComplete=True
    eachShop.PHHDeliveryDate=PHHDeliveryDate
    eachShop.AAYDeliveryDate=AAYDeliveryDate
    eachShop.isProcessed=True
    eachShop.save()
    logger.info("Processing statusID: %s, state: %s fpsCode: %s district: %s, block: %s ShopName : %s fpsMonth:%s fpsYear: %s" % (str(statusID),stateName,fpsCode,districtName,blockName,fpsName,str(fpsMonth),str(fpsYear)))

  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
