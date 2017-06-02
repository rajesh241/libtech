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
def validateFPSStatus(logger,myhtml):
  status=None
  summaryTable=None
  deliveryTable=None
  searchText='class="newFormTheme"'
  replaceText='class="newFormTheme" id="newFormTheme"'
  htmlsoup=BeautifulSoup(myhtml,"html.parser")
  tables=htmlsoup.findAll('table',{ "class" : "newFormTheme" })
  for table in tables:
    if "Locality" in str(table):
      logger.info("Found Summary Table")
      summaryTable=table
    elif "SIO Status" in str(table):
      logger.info("Delivery Table Found")
      deliveryTable=table
  if (summaryTable is not None) and (deliveryTable is not None):
    status=1

  return status,summaryTable,deliveryTable
#  fpsHtml=fpsHtml.decode("UTF-8").replace(searchText,replaceText)

def main():
  httplib2.debuglevel = 1
  monthLabels=['0','JAN','FEB','MAR','APR','MAY','JUNE','JULY','AUG','SEP','OCT','NOV','DEC']
  searchText='class="newFormTheme"'
  replaceText='class="newFormTheme" id="newFormTheme"'
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  if args['fpsCode']:
    incode=args['fpsCode']
    myShops=FPSStatus.objects.filter(fpsShop__fpsCode=incode,isComplete=False)
  else:
    myShops=FPSStatus.objects.filter(isComplete=False).order_by('isDownloaded')
  for eachShop in myShops:
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
    logger.info("Processing state: %s fpsCode: %s district: %s, block: %s ShopName : %s fpsMonth:%s fpsYear: %s" % (stateName,fpsCode,districtName,blockName,fpsName,str(fpsMonth),str(fpsYear)))
    i=0

    hlib = httplib2.Http('.cache')
    url = 'http://sfc.bihar.gov.in/fpshopsSummaryDetails.htm'
 
    data = {
     'mode':'searchFPShopDetails',
     'dyna(state_id)':'10',
     'dyna(fpsCode)':'',
     'dyna(scheme_code)':'',
     'dyna(year)':fpsYear,
     'dyna(month)':fpsMonth,
     'dyna(district_id)':districtCode,
     'dyna(block_id)':blockCode,
     'dyna(fpshop_id)':fpsCode,
     }
 
    #print(urlencode(data))
    response, htmlsource = hlib.request(url, 'POST', urlencode(data), headers = {'Content-Type': 'application/x-www-form-urlencoded'})
    logger.info("Download Response : %s" % response)
    if response['status'] == '200':
      logger.info("Status is 200")
      with open("/tmp/c.html","wb") as f:
        f.write(htmlsource)
        error,summaryTable,deliveryTable=validateFPSStatus(logger,htmlsource)
        if error is not None:
          logger.info("Found Both the Tables")
          title="%s_%s-%s" % (str(fpsYear),fpsMonthName,fpsName)
          outhtml=''
          outhtml+=stripTableAttributesOrdered(summaryTable,"summaryTable")
          outhtml+=stripTableAttributesOrdered(deliveryTable,"deliveryTable")
          outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
          try:
            outhtml=outhtml.encode("UTF-8")
          except:
            outhtml=outhtml
          filename="%s-%s-%s.html" % (fpsSlug,fpsMonthName,str(fpsYear))
          eachShop.statusFile.save(filename, ContentFile(outhtml))
          eachShop.downloadAttemptDate=timezone.now()
          eachShop.isDownloaded=True
          eachShop.isProcessed=False
          eachShop.save()
        else:
          eachShop.downloadAttemptDate=timezone.now()
          eachShop.save()
  #   logger.info("File Name : %s " % filename)
  #   title="%s_%s-%s" % (str(fpsYear),fpsMonthName,fpsNameFiltered)
  #   fpsHtml=fpsHtml.decode("UTF-8").replace(searchText,replaceText)
  #   fpsHtml=fpsHtml.encode("UTF-8")
  #   tableID=['newFormTheme']
  #   fpsHtmlWeb=alterHTMLTables(fpsHtml,title,tableID)
  #   logger.info(filename)
  #   mpa = dict.fromkeys(range(32))
  #   filename=filename.translate(mpa)
  #   writeFile3(filename,fpsHtmlWeb.encode("UTF-8"))
 
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
