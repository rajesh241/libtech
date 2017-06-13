from bs4 import BeautifulSoup
from datetime import datetime,date
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.parse import urlparse,parse_qs
import os
import requests
import sys
import re
from customSettings import repoDir,djangoDir,djangoSettings,jobCardRegisterTimeThreshold
import lxml.html
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getCurrentFinYear,savePanchayatReport,table2csv
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import F,Q

os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Village

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
  parser.add_argument('-nbc', '--nicBlockCode', help='NIC BlockCode for which the numbster needs to be downloaded', required=True)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  display = displayInitialize(args['visible'])
  driver = driverInitialize(args['browser'])
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1
  nicBlockCode=args["nicBlockCode"]
  myBlock=Block.objects.filter(code=nicBlockCode).first()
  blockCode=myBlock.tcode
  blockName=myBlock.name
  url="http://www.nrega.telangana.gov.in/Nregs/FrontServlet?requestType=SmartCardreport_engRH&actionVal=MobnumberStatus&id=%s&Retype=null&type=null&file=%s"  % (blockCode,blockName)
  logger.info(url)
  try:
    driver.get(url)
    driver.get(url)
    myhtml = driver.page_source
    error=0
  except:
    error=1

  if error==0:
    logger.info("No Error")
#   dom =  lxml.html.fromstring(myhtml)
#   for link in dom.xpath('//a/@href'): # select the url in href for all a tags(links)
#     print(link)
    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    table=htmlsoup.find('table',id="sortable")
    if table is not None:
      print("Found")
 
      for link in table.find_all('a'):
        logger.info(link['href'])
        panchayatLink="http://www.nrega.telangana.gov.in"+link['href']
        myArray=panchayatLink.split("file=")
        panchayatName=myArray[1]
        logger.info(panchayatName+panchayatLink)
        myPanchayat=Panchayat.objects.filter(block=myBlock,name=panchayatName).first()
        if myPanchayat is not None:
          try:
            driver.get(panchayatLink)
            driver.get(panchayatLink)
            phtml = driver.page_source
            perror=0
          except:
            perror=1

          if perror==0:
            logger.info("No Error") 
            phtmlsoup=BeautifulSoup(phtml,"html.parser")
            ptable=phtmlsoup.find('table',id="sortable")
            if ptable is not None:
              print("Found")
          
              for link in ptable.find_all('a'):
                logger.info(link['href'])
                villageLink="http://www.nrega.telangana.gov.in"+link['href']
                myArray=villageLink.split("file=")
                villageName=myArray[1]
                par = parse_qs(urlparse(villageLink).query)
                villageID=str(par['id'][0]).lstrip().rstrip()
                villageName=str(par['file'][0])
                logger.info(villageName+villageID)
                logger.info(par)
                logger.info(len(villageID))
                myVillage=Village.objects.filter(tcode=villageID).first()
                if myVillage is None:
                  Village.objects.create(tcode=villageID)
                myVillage=Village.objects.filter(tcode=villageID).first()
                myVillage.name=villageName
                myVillage.code=villageID
                myVillage.panchayat=myPanchayat
                myVillage.save()
       
        

  driverFinalize(driver)
  displayFinalize(display)
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
