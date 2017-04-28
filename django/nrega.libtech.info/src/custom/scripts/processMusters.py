from bs4 import BeautifulSoup
from datetime import datetime,date
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
import os
import sys
import re
import time
from customSettings import repoDir,djangoDir,djangoSettings

sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getjcNumber
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.db.models import F
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Applicant,Muster,WorkDetail,Wagelist

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='This Script is for Processing Muster')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-s', '--stateCode', help='StateCode for which the numbster needs to be downloaded', required=False)

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
  stateCode=args['stateCode']
  if stateCode is not None:
    logger.info("StateCode is %s" % stateCode)
    myMusters=Muster.objects.filter(isRequired=1,isDownloaded=1,isProcessed=0,panchayat__crawlRequirement="FULL",panchayat__block__district__state__stateCode=stateCode)[:limit] 
  else:
    myMusters=Muster.objects.filter(isRequired=1,isDownloaded=1,isProcessed=0)[:limit] 
  for eachMuster in myMusters:
    logger.info("MusterNo: %s, blockCode: %s, finyear: %s workName:%s" % (eachMuster.musterNo,eachMuster.block.fullBlockCode,eachMuster.finyear,eachMuster.workName))
    logger.info(eachMuster.panchayat.fullPanchayatCode+eachMuster.panchayat.crawlRequirement+eachMuster.panchayat.name)
    myhtml=eachMuster.musterFile.read()
    stateShortCode=eachMuster.block.district.state.stateShortCode
    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    mytable=htmlsoup.find('table',id="musterDetails")
    tr_list = mytable.findAll('tr')
    for tr in tr_list: #This loop is to find staus Index
      cols = tr.findAll('th')
      if len(cols) > 7:
        i=0
        while i < len(cols):
          value="".join(cols[i].text.split())
          if "Status" in value:
            statusindex=i
          i=i+1
    isComplete=1
    totalCount=0
    totalPending=0
    reMatchString="%s-" % (stateShortCode)
    for i in range(len(tr_list)):
      cols=tr_list[i].findAll("td")
      if len(cols) > 7:
        nameandjobcard=cols[1].text.lstrip().rstrip()
        if stateShortCode in nameandjobcard:
          totalCount=totalCount+1
          status=cols[statusindex].text.lstrip().rstrip()
          if status != 'Credited':
            totalPending=totalPending+1
            isComplete=0      
          musterIndex=cols[0].text.lstrip().rstrip()
          nameandjobcard=cols[1].text.lstrip().rstrip()
          nameandjobcard=nameandjobcard.replace('\n',' ')
          nameandjobcard=nameandjobcard.replace("\\","")
          nameandjobcardarray=re.match(r'(.*)'+reMatchString+'(.*)',nameandjobcard)
          name_relationship=nameandjobcardarray.groups()[0]
          name=name_relationship.split("(")[0]
          accountno=cols[statusindex-5].text.lstrip().rstrip()
          jobcard=reMatchString+nameandjobcardarray.groups()[1]
          totalWage=cols[statusindex-6].text.lstrip().rstrip()
          dayWage=cols[statusindex-10].text.lstrip().rstrip()
          daysWorked=cols[statusindex-11].text.lstrip().rstrip()
          wagelistNo=cols[statusindex-1].text.lstrip().rstrip()
          creditedDateString=cols[statusindex+1].text.lstrip().rstrip()
          if creditedDateString != '':
            creditedDate = time.strptime(creditedDateString, '%d/%m/%Y')
            creditedDate = time.strftime('%Y-%m-%d', creditedDate)
          else:
            creditedDate=None
        myWDRecord=WorkDetail.objects.filter(muster=eachMuster,musterIndex=musterIndex).first()
        if myWDRecord is None:
          logger.info("New Record Created")
          WorkDetail.objects.create(muster=eachMuster,musterIndex=musterIndex)
        myWDRecord=WorkDetail.objects.filter(muster=eachMuster,musterIndex=musterIndex).first()
        
        matchedWagelist=Wagelist.objects.filter(wagelistNo=wagelistNo,block=eachMuster.panchayat.block,finyear=eachMuster.finyear).first()
        if matchedWagelist is not None:
          logger.info("Wagelist Found")
        else:
          Wagelist.objects.create(wagelistNo=wagelistNo,block=eachMuster.panchayat.block,finyear=eachMuster.finyear)
        matchedWagelist=Wagelist.objects.filter(wagelistNo=wagelistNo,block=eachMuster.panchayat.block,finyear=eachMuster.finyear).first()

        myWDRecord.wagelist=matchedWagelist 
        
        matchedApplicants=Applicant.objects.filter(jobcard=jobcard,name=name)
        logger.info("jobcard %s name: %s " % (jobcard,name)) 
        if len(matchedApplicants) == 1:
          logger.info("MatchedApplicant Found")
          myWDRecord.applicant=matchedApplicants.first()
        
        myWDRecord.zname=name
        myWDRecord.zjobcard=jobcard
        myWDRecord.zaccountNo=accountno
        myWDRecord.totalWage=totalWage
        myWDRecord.dayWage=dayWage
        myWDRecord.daysWorked=daysWorked
        myWDRecord.creditedDate=creditedDate
        myWDRecord.musterStatus=status 
        myWDRecord.save()
    eachMuster.isComplete=isComplete
    eachMuster.isProcessed=1
    eachMuster.save()
  logger.info("...END PROCESSING") 
  exit(0)

if __name__ == '__main__':
  main()
