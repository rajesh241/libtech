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
from nrega.models import State,District,Block,Panchayat
# This is so models get loaded.
def getURL(url):
  retry=0
  myhtml=''
  status=''
  while retry < 3 :
    retry=retry+1
    try: 
      r=requests.get(url)
      myhtml=r.text
      status=r.status_code
      error=0
    except:
      error=1
    if error == 0:
      break
  return status,myhtml

def getDistrictURL(crawlIP,stateName,stateCode,districtName,fullDistrictCode):
  url="http://%s/netnrega/homedist.aspx?state_name=%s&state_code=%s&District_code=%s&District_name=%s&lflag=eng" % (crawlIP,stateName,stateCode,fullDistrictCode,districtName)
  return url
def getBlockURL(crawlIP,stateName,stateCode,districtName,fullDistrictCode,blockName,fullBlockCode):
  finyear='2015-2016'
  url="http://%s/netnrega/Progofficer/PoIndexFrame.aspx?flag_debited=R&lflag=Eng&District_Code=%s&district_name=%s&state_name=%s&state_Code=%s&finyear=%s&check=1&block_name=%s&Block_Code=%s" %(crawlIP,fullDistrictCode,districtName,stateName,stateCode,finyear,blockName,fullBlockCode)
  return url
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
  
  allDistricts=District.objects.all()
  #allDistricts=District.objects.filter(name="surguja")
  for eachDistrict in allDistricts:
    districtName=eachDistrict.name
    fullDistrictCode=eachDistrict.fullDistrictCode
    stateName=eachDistrict.state.name
    crawlIP=eachDistrict.state.crawlIP
    stateCode=eachDistrict.state.stateCode
    districtURL=getDistrictURL(crawlIP,stateName,stateCode,districtName,fullDistrictCode)
    logger.info("**************************")
    logger.info("Processing: stateName: %s , districtName %s, districtURL %s " % (stateName,districtName,districtURL))
    logger.info("**************************")

    blockURLStatus,blockHTML=getURL(districtURL)
    logger.info("District URL Status; %s " % (blockURLStatus))
    if blockURLStatus == 200 :
      htmlsoup=BeautifulSoup(blockHTML)
      table=htmlsoup.find('table',id="gvdpc")
      if table is not None:
        rows = table.findAll('tr')
        for row in rows:
          columns=row.findAll('td')
          for column in columns:
            r=re.findall('Block_Code=(.*?)\"',str(column))
            fullBlockCode=r[0]
            r=re.findall('block_name=(.*?)\&',str(column))
            rawBlockName=r[0]
            logger.info("stateName: %s, districtName:%s,Block Code: %s BlockName : %s" % (stateName,districtName,fullBlockCode,rawBlockName))
            blocks=Block.objects.filter(fullBlockCode=fullBlockCode)
            if len(blocks)==0:
              logger.info("No Block Found")
              Block.objects.create(name=rawBlockName,fullBlockCode=fullBlockCode,district=eachDistrict)
            else:
              myblock=blocks.first()
              myblock.name=rawBlockName
              myblock.district=eachDistrict
              myblock.save()
     
            blocks=Block.objects.filter(fullBlockCode=fullBlockCode)
            myblock=blocks.first()

            blockURL=getBlockURL(crawlIP,stateName,stateCode,districtName,fullDistrictCode,rawBlockName,fullBlockCode)
            panchayatURLStatus,htmlsource1=getURL(blockURL)
            if panchayatURLStatus == 200:
              htmlsoup1=BeautifulSoup(htmlsource1)
              table1=htmlsoup1.find('table',id="ctl00_ContentPlaceHolder1_gvpanch")
              try:
                table1.findAll('a')    
                noPanchayat=0
              except:
                noPanchayat=1
              if noPanchayat == 0:
                allPanchayatLinks=table1.findAll('a')
                if len(allPanchayatLinks) > 0:
                  for eachPanchayat in allPanchayatLinks:
                    rawPanchayatName=eachPanchayat.contents[0]
                    panchayatLink=eachPanchayat.get('href')
                    getPanchayat=re.findall(r'(?:Panchayat_Code=)\d{10}',panchayatLink)
                    fullPanchayatCode=getPanchayat[0].replace("Panchayat_Code=","")
                    logger.info("stateName: %s, districtName: %s, blockName: %s, Panchayat` Code: %s PanchayatName : %s" % (stateName,districtName,rawBlockName,fullPanchayatCode,rawPanchayatName))

                    panchayats=Panchayat.objects.filter(fullPanchayatCode=fullPanchayatCode)
                    if len(panchayats)==0:
                      logger.info("No Panchayat Found")
                      Panchayat.objects.create(name=rawPanchayatName,fullPanchayatCode=fullPanchayatCode,block=myblock)
                    else:
                      mypanchayat=panchayats.first()
                      mypanchayat.name=rawPanchayatName
                      mypanchayat.block=myblock
                      mypanchayat.save()
     

  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
