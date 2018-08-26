
from bs4 import BeautifulSoup
from datetime import datetime,date
import requests
import os
import sys
import re
import time
from subprocess import call,Popen,check_output,PIPE
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
from customSettings import repoDir,djangoDir,djangoSettings,startFinYear,panchayatCrawlThreshold,panchayatRetryThreshold,telanganaStateCode,panchayatAttemptRetryThreshold,apStateCode,crawlRetryThreshold,logDir
#from crawlFunctions import crawlPanchayat,crawlPanchayatTelangana,libtechCrawler
from libtechCrawler import libtechCrawler
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getCurrentFinYear,savePanchayatReport,table2csv,getFullFinYear
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import F,Q,Sum,Count
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster,LibtechTag,CrawlQueue,CrawlState

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-downloadLimit', '--downloadLimit', help='Limit on the number of results', required=False)
  parser.add_argument('-s', '--stateCode', help='State for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-sf', '--startFinYear', help='From which financial year data needs to be crawled default is 2015-2016', required=False)
  parser.add_argument('-step', '--step', help='Step for which the script needs to run', required=False)
  parser.add_argument('-pc', '--panchayatCode', help='Panchayat for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-qid', '--qid', help='Queue Id for which this needs to be run', required=False)
  parser.add_argument('-bc', '--blockCode', help='Panchayat for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-m', '--manage', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-e', '--execute', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-p', '--populate', help='Populate CrawlQueue', required=False,action='store_const', const=1)
  parser.add_argument('-f', '--force', help='Force Run a step', required=False,action='store_const', const=1)
  parser.add_argument('-se', '--singleExecute', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-i', '--initiateCrawl', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-d', '--debug', help='Debug Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-t', '--test', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)

  args = vars(parser.parse_args())
  return args
    
def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  if args['initiateCrawl']:
    logger.debug("This script is going to initiate crawl")
    if args['step']:
      crawlStates=CrawlState.objects.filter(name=args['step'])
    else:
      #crawlStates=CrawlState.objects.all()
      crawlStates=CrawlState.objects.filter(isActive=True)
    for eachState in crawlStates:
      crawlProcessTimeThreshold=eachState.threshold
      curStateName=eachState.name
      logfile="%s/%s.log" % (logDir,curStateName)
      debuglogfile="/%s/debug/%s_%s.log" % (logDir,curStateName,str(int(time.time())))
      logger.debug("Curent state name is %s " % curStateName)
      curhour=datetime.now().hour
      nicTimeBand=False
      if (curhour >=6) and (curhour <= 20):
        nicTimeBand=True
      scriptDir='%s/custom/crawlScripts/' % djangoDir
      
      if ((eachState.nicHourRestriction==False) or ((eachState.nicHourRestriction==True) and (nicTimeBand==True))):
        cmd="python %s/crawlMain.py -e -l debug -step %s " % (scriptDir,curStateName)
#        cmd=scriptName
        p1 = Popen(['pgrep', '-f', cmd], stdout=PIPE)
    #    logger.debug(p1.communicate())
        mypid = p1.communicate()[0].decode("utf-8").lstrip().rstrip()
        logger.debug("Exsiting PID for this command  %s is %s " % (curStateName,str(mypid)))
        if (mypid == ""):
          logger.debug("We are going to launch this program %s" % cmd)
          proc = Popen([cmd], shell=True,stdin=None, stdout=None, stderr=None, close_fds=True)
        else:
          mycmd='ps -o etimes= -p %s ' % mypid
          p1 = Popen([mycmd], stdout=PIPE,shell=True)
          output = p1.communicate()[0].decode("utf-8").lstrip().rstrip()
          logger.debug(output)
          if int(output) > crawlProcessTimeThreshold:
            mycmd="kill -9 %s " % mypid
            mycmd="pkill -P %s " % mypid
            logger.debug(mycmd)
            p1 = Popen([mycmd], stdout=PIPE,shell=True)
            output = p1.communicate()[0].decode("utf-8").lstrip().rstrip()
            logger.debug(output)
            mycmd="cp %s %s " % (logfile,debuglogfile)
            p1 = Popen([mycmd], stdout=PIPE,shell=True)
            output = p1.communicate()[0].decode("utf-8").lstrip().rstrip()
            logger.debug(output)

  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
