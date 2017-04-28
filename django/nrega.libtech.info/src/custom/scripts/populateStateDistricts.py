from bs4 import BeautifulSoup
import requests
import os
import sys
import re
import urllib.request
import django
from django.core.wsgi import get_wsgi_application

from customSettings import repoDir,djangoDir,djangoSettings
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
from wrappers.logger import loggerFetch
sys.path.append(djangoDir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
# This is so Django knows where to find stuff.
# This is so my local_settings.py gets loaded.
django.setup()
from nrega.models import State,District
# This is so models get loaded.

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  stateName="Gujarat"
  stateCode='44'

  url="http://nrega.nic.in/netnrega/sthome.aspx"
  r=requests.get(url)
  myhtml=r.text
  htmlsoup=BeautifulSoup(myhtml)
  tables=htmlsoup.findAll('table')
  for table in tables:
    if "BIHAR" in str(table):
       logger.info("The Table Found")
       links=table.findAll('a')
       
       logger.info(str(len(links)))
       for link in links:
         #if "BIHAR" in str(link):
         if "state_name" in str(link):
           stateURL=link['href']+"&lflag=eng"
           stateURL=urllib.request.unquote(stateURL)
           logger.info(stateURL)
           r=re.findall('http://(.*?)\/',stateURL)
           crawlIP=r[0]
           r=re.findall('state_code=(.*?)\&',stateURL)
           stateCode=r[0]
           r=re.findall('state_name=(.*?)\&',stateURL)
           stateName=r[0]
           logger.info("State Name : %s " ,stateName)
           logger.info("State Code : %s " ,stateCode) 
           logger.info("Crawl IP : %s " ,crawlIP)
           states=State.objects.filter(stateCode=stateCode)
           if len(states)==0:
             logger.info("No State Found")
             State.objects.create(name=stateName,stateCode=stateCode)
           else:
             mystate=states.first()
             print(mystate)
             mystate.name=stateName
             mystate.crawlIP=crawlIP
             mystate.save()
            
           states=State.objects.filter(stateCode=stateCode)
           mystate=states.first()

           r=requests.get(stateURL)
           myhtml=r.text
           htmlsoup=BeautifulSoup(myhtml)
           table=htmlsoup.find('table',id="gvdist")
           if table is not None:
             distLinks = table.findAll('a')
             for distLink in distLinks:
               districtURL=distLink['href']
               districtURL=urllib.request.unquote(districtURL)
               #r=re.findall('http://(.*?)\/',districtURL)
               #crawlIP=r[0]
               logger.info(districtURL)
               districtURLPrefix="http://%s/netnrega/" % crawlIP
               r=re.findall('district_code=(.*?)\&',districtURL)
               fullDistrictCode=r[0]
               r=re.findall('district_name=(.*?)\&',districtURL)
               rawDistrictName=r[0]
               logger.info("District Code : %s " ,fullDistrictCode) 
               logger.info("District Name : %s " ,rawDistrictName) 
             
               districts=District.objects.filter(fullDistrictCode=fullDistrictCode)
               if len(districts)==0:
                 logger.info("No District Found")
                 District.objects.create(name=rawDistrictName,fullDistrictCode=fullDistrictCode,state=mystate)
               else:
                 mydistrict=districts.first()
                 mydistrict.name=rawDistrictName
                 mydistrict.state=mystate
                 mydistrict.save()
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
