from bs4 import BeautifulSoup
import requests
import os
import sys
import re
import urllib.request
import django
import json
from django.core.wsgi import get_wsgi_application

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
from customSettings import repoDir,djangoDir,djangoSettings
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
from wrappers.logger import loggerFetch
sys.path.append(djangoDir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
# This is so Django knows where to find stuff.
# This is so my local_settings.py gets loaded.
django.setup()
from nrega.models import State,District,Block,Panchayat,CrawlState


def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-n', '--name', help='Enter state,district block or panchayat', required=False)
  parser.add_argument('-location', '--location', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-crawlState', '--crawlState', help='Make the browser visible', required=False, action='store_const', const=1)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  if args['crawlState']:
    logger.info("Going to Populate Crawl State Codes")
    with open('/tmp/crawlStates.csv') as fp:
      for line in fp:
        line=line.lstrip().rstrip()
        if line != '':
          lineArray=line.split(",")
          logger.info(lineArray)
          name=lineArray[0]
          sequence=int(lineArray[1])
          crawlType=lineArray[2]
          if lineArray[3] == '1':
            needsQueueManager=True
          else:
            needsQueueManager=False
          if lineArray[4] == '1':
            nicHourRestrict=True
          else:
            nicHourRestrict=False
          CrawlState.objects.create(name=name,crawlType=crawlType,sequence=sequence,needsQueueManager=needsQueueManager,nicHourRestriction=nicHourRestrict) 
  if args['location']:
    if args['name']:
      name=args['name']
    else:
      name='block'
    jsonName='%ss.json' % (name)
    logger.info("Json file name is %s " % (jsonName))
    json_data=open(jsonName).read()
    d = json.loads(json_data)
    if name=='panchayat':
      for key,values in d.items():
        panchayatCode=key
        panchayatName=values['name']
        blockCode=values['blockCode']
        logger.info(key)
        eachBlock=Block.objects.filter(code=blockCode).first()
        if eachBlock is not None:
          eachPanchayat=Panchayat.objects.filter(code=panchayatCode).first()
          if eachPanchayat is None:
            Panchayat.objects.create(block=eachBlock,code=panchayatCode,name=panchayatName)
          else:
            eachPanchayat.name=panchayatName
            eachPanchayat.block=eachBlock
            eachPanchayat.save()
        else:
          logger.info("Block with code %s does not exists" % blockCode)
    
    if name=='block':
      for key,values in d.items():
        blockCode=key
        blockName=values['name']
        districtCode=values['districtCode']
        eachDistrict=District.objects.filter(code=districtCode).first()
        if eachDistrict is not None:
          eachBlock=Block.objects.filter(code=blockCode).first()
          if eachBlock is None:
            eachBlock=Block.objects.create(code=blockCode,district=eachDistrict,name=blockName)
          else:
            eachBlock.district=eachDistrict
            eachBlock.name=blockName
            eachBlock.save()
        else:
          logger.info("District with code %s does not exist" % (districtCode))
    
    if name=='district':
      for key,values in d.items():
        districtCode=key
        districtName=values['name']
        stateCode=values['stateCode']
        eachState=State.objects.filter(code=stateCode).first()
        if eachState is not None:
          eachDistrict=District.objects.filter(code=districtCode).first()
          if eachDistrict is None:
            eachDistrict=District.objects.create(code=districtCode,state=eachState,name=districtName)
          else:
            eachDisctrict.state=eachState
            eachDistrict.name=districtName
            eachDistrict.save()
        else:
          logger.info("State with code %s does not exist" % (stateCode))
    
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
