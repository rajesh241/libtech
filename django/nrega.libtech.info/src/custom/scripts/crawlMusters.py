from bs4 import BeautifulSoup
from datetime import datetime,date
import requests
import os
import sys
import re
import time
from customSettings import repoDir,djangoDir,djangoSettings,startFinYear

sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getFullFinYear,getCurrentFinYear
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-s', '--stateCode', help='State for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-p', '--panchayatCode', help='Panchayat for which the delayed payment report needs to be crawld', required=False)

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
  
  endFinYear=getCurrentFinYear()

  regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
  stateCode=args['stateCode']
  panchayatCode=args['panchayatCode']
  if panchayatCode is not None:
    myPanchayats=Panchayat.objects.filter(crawlRequirement='FULL',block__district__state__isNIC=True,code=panchayatCode).order_by('musterCrawlDate')[:limit]
  else: 
    if stateCode is None:
      myPanchayats=Panchayat.objects.filter(crawlRequirement='FULL',block__district__state__isNIC=True).order_by('musterCrawlDate')[:limit]
    else:
      myPanchayats=Panchayat.objects.filter(status='2',crawlRequirement='FULL',block__district__state__code=stateCode,block__district__state__isNIC=True).order_by('musterCrawlDate')[:limit]
#  myPanchayats=Panchayat.objects.filter(fullPanchayatCode='3405003010').order_by('jobcardCrawlDate')[:limit]
#  myPanchayats=Panchayat.objects.filter(fullPanchayatCode='3405003010').order_by('jobcardCrawlDate')[:limit]
  for eachPanchayat in myPanchayats:
    for finyear in range(int(startFinYear),int(endFinYear)+1):
      finyear=str(finyear)
      logger.info("Processing Financial Year : %s " % str(finyear))
      fullfinyear=getFullFinYear(finyear)
      logger.info("Processing : panchayat: %s " % (eachPanchayat.name))
      stateCode=eachPanchayat.block.district.state.code
      fullDistrictCode=eachPanchayat.block.district.code
      fullBlockCode=eachPanchayat.block.code
      fullPanchayatCode=eachPanchayat.code
      districtName=eachPanchayat.block.district.name
      blockName=eachPanchayat.block.name
      stateName=eachPanchayat.block.district.state.name
      crawlIP=eachPanchayat.block.district.state.crawlIP
      panchayatName=eachPanchayat.name
      musterType='10'
      url="http://"+crawlIP+"/netnrega/state_html/emuster_wage_rep1.aspx?type="+str(musterType)+"&lflag=eng&state_name="+stateName+"&district_name="+districtName+"&block_name="+blockName+"&panchayat_name="+panchayatName+"&panchayat_code="+fullPanchayatCode+"&fin_year="+fullfinyear
      logger.info(url)
      try:
        r  = requests.get(url)
        error=0
      except requests.exceptions.RequestException as e:  # This is the correct syntax
        logger.info(e) 
        error=1
      if error==0:
        curtime = time.strftime('%Y-%m-%d %H:%M:%S')
        htmlsource=r.text
        htmlsource1=re.sub(regex,"",htmlsource)
        htmlsoup=BeautifulSoup(htmlsource1,"html.parser")
        try:
          table=htmlsoup.find('table',bordercolor="green")
          rows = table.findAll('tr')
          errorflag=0
        except:
          status=0
          errorflag=1
        if errorflag==0:
          for tr in rows:
            cols = tr.findAll('td')
            tdtext=''
            district= cols[1].string.strip()
            block= cols[2].string.strip()
            panchayat= cols[3].string.strip()
            worknameworkcode=cols[5].text
            if district!="District":
              emusterno="".join(cols[6].text.split())
#              logger.info(emusterno)
              datefromdateto="".join(cols[7].text.split())
              datefromstring=datefromdateto[0:datefromdateto.index("-")]
              datetostring=datefromdateto[datefromdateto.index("-") +2:len(datefromdateto)]
              if datefromstring != '':
                datefrom = time.strptime(datefromstring, '%d/%m/%Y')
                datefrom = time.strftime('%Y-%m-%d', datefrom)
              else:
                datefrom=''
              if datetostring != '':
                dateto = time.strptime(datetostring, '%d/%m/%Y')
                dateto = time.strftime('%Y-%m-%d', dateto)
              else:
                dateto=''
              #worknameworkcodearray=re.match(r'(.*)\(330(.*)\)',worknameworkcode)
              worknameworkcodearray=re.match(r'(.*)\('+stateCode+r'(.*)\)',worknameworkcode)
              if worknameworkcodearray is not None:
                workName=worknameworkcodearray.groups()[0]
                workCode=stateCode+worknameworkcodearray.groups()[1]
                logger.info(emusterno+" "+datefromstring+"  "+datetostring+"  "+workCode)
                musterURL="http://%s/netnrega/citizen_html/musternew.aspx?state_name=%s&district_name=%s&block_name=%s&panchayat_name=%s&workcode=%s&panchayat_code=%s&msrno=%s&finyear=%s&dtfrm=%s&dtto=%s&wn=%s&id=1" % (eachPanchayat.block.district.state.crawlIP,stateName,districtName,blockName,panchayatName,workCode,fullPanchayatCode,emusterno,fullfinyear,datefromstring,datetostring,workName.replace(" ","+"))
                #logger.info(musterURL)
                myMuster=Muster.objects.filter(finyear=finyear,musterNo=emusterno,block__code=fullBlockCode).first()
                if myMuster is  None:
                  #logger.info("Muster does not exists") 
                  Muster.objects.create(block=eachPanchayat.block,finyear=finyear,musterNo=emusterno)
                myMuster=Muster.objects.filter(finyear=finyear,musterNo=emusterno,block__code=fullBlockCode).first()
                myMuster.dateFrom=datefrom
                myMuster.dateTo=dateto
                myMuster.workCode=workCode
                myMuster.workName=workName 
                myMuster.musterType='10'
                myMuster.musterURL=musterURL
                myMuster.isRequired=1
                myMuster.panchayat=eachPanchayat
                myMuster.save()
    eachPanchayat.musterCrawlDate=datetime.now()
    eachPanchayat.musterCrawlDate=timezone.now()
    eachPanchayat.status='3'
    eachPanchayat.save()
     # query="insert into musters (fullBlockCode,musterNo,stateCode,districtCode,blockCode,panchayatCode,musterType,finyear,workCode,workName,dateFrom,dateTo,crawlDate) values ('"+fullBlockCode+"','"+emusterno+"','"+stateCode+"','"+districtCode+"','"+blockCode+"','"+panchayatCode+"','"+musterType+"','"+finyear+"','"+workCode+"','"+workName+"','"+datefrom+"','"+dateto+"',NOW())"
    logger.info("Processing StateCode %s, fullDistrictCode : %s, fullBlockCode : %s, fullPanchayatCode: %s " % (stateCode,fullDistrictCode,fullBlockCode,fullPanchayatCode))
 
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
