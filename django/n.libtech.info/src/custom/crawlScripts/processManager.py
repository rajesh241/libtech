
from bs4 import BeautifulSoup
from datetime import datetime,date
import requests
import os
import sys
import re
import time
import importlib
from subprocess import call,Popen,check_output,PIPE
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
from customSettings import repoDir,djangoDir,djangoSettings,startFinYear,panchayatCrawlThreshold,panchayatRetryThreshold,telanganaStateCode,panchayatAttemptRetryThreshold,apStateCode,crawlRetryThreshold,crawlProcessTimeThreshold,logDir
#from crawlFunctions import crawlPanchayat,crawlPanchayatTelangana,libtechCrawler
from libtechCrawler import libtechCrawler
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from libtechInit import libtechLoggerFetch
from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getCurrentFinYear,savePanchayatReport,table2csv,getFullFinYear
from wrappers.logger import loggerFetch
import crawl,misc
import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import F,Q,Sum,Count
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster,LibtechTag,CrawlQueue,CrawlState,Task,LibtechProcess

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-n', '--numOfProcess', help='No of Processes that need to be run', required=False)
  parser.add_argument('-downloadLimit', '--downloadLimit', help='Limit on the number of results', required=False)
  parser.add_argument('-s', '--stateCode', help='State for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-sf', '--startFinYear', help='From which financial year data needs to be crawled default is 2015-2016', required=False)
  parser.add_argument('-step', '--step', help='Step for which the script needs to run', required=False)
  parser.add_argument('-pc', '--panchayatCode', help='Panchayat for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-pid', '--pid', help='Queue Id for which this needs to be run', required=False)
  parser.add_argument('-bc', '--blockCode', help='Panchayat for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-m', '--manage', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-e', '--execute', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-p', '--populate', help='Populate CrawlTask', required=False,action='store_const', const=1)
  parser.add_argument('-f', '--force', help='Force Run a step', required=False,action='store_const', const=1)
  parser.add_argument('-se', '--singleExecute', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-i', '--initiateCrawl', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-r', '--run', help='Debug Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-t', '--test', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)

  args = vars(parser.parse_args())
  return args

def runTask(logger,myProcess=None):
  if myProcess is not None: 
    myProcess.save()
  myTask=Task.objects.filter(isComplete=False,isError=False,inProgress=False).order_by("modified").first()
  if myTask is not None:
    myTask.inProgress=True
    myTask.save()
    if myTask.crawlState is not None:
      funcName=myTask.crawlState.name
    elif myTask.processName is not None:
      funcName=myTask.processName
    else:
      funcName=None
    libName=myTask.libName
    logger.info("Running Task %s-%s Task ID %s" % (libName,funcName,str(myTask.id)))
    objID=myTask.objID
    finyear=myTask.finyear
    if (funcName is not None) and (libName is not None):
      module = __import__(libName)
      importlib.reload(module)
      isComplete=getattr(module,funcName)(logger,objID,finyear=finyear)
      myTask.isComplete=isComplete
    else:
      myTask.isError=True
    myTask.inProgress=False
    myTask.save()
  else:
    logger.debug("No tasks to run")
    time.sleep(10)
  

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))

  if args['run']:
    pid=args['pid']
    if pid is not None:
      logFileName="p%s.log" % (str(pid))
      processLogger = libtechLoggerFetch('debug',filename=logFileName)
      myProcess=LibtechProcess.objects.filter(pid=pid).first()
      if myProcess is None:
        myProcess=LibtechProcess.objects.create(pid=pid)
      myProcess.save()
      while True:
        try:
          runTask(processLogger,myProcess=myProcess)
        except:
          processLogger.exception('Got exception on main handler')
          raise
          

  if args['manage']:
    scriptDir='%s/custom/crawlScripts/' % djangoDir
    n=1
    if args['numOfProcess']:
      n=int(args['numOfProcess'])
    for pid in range(n):
      pid=pid+1
      logfile="%s/p%s.log" % (logDir,str(pid))
      
      cmd="python %s/processManager.py -r -pid %s " % (scriptDir,str(pid))
      p1 = Popen(['pgrep', '-f', cmd], stdout=PIPE)
      mypid = p1.communicate()[0].decode("utf-8").lstrip().rstrip()
      logger.debug("Exsiting PID for this command  %s is %s " % (str(pid),str(mypid)))
      if (mypid == ""):
        logger.debug("We are going to launch this program %s" % cmd)
        proc = Popen([cmd], shell=True,stdin=None, stdout=None, stderr=None, close_fds=True)
      else:
        mycmd='ps -o etimes= -p %s ' % mypid
        p1 = Popen([mycmd], stdout=PIPE,shell=True)
        output = p1.communicate()[0].decode("utf-8").lstrip().rstrip()
        logger.debug(output)
        if int(output) > crawlProcessTimeThreshold:
          mycmd="pkill -P %s " % mypid
          logger.debug(mycmd)
          p1 = Popen([mycmd], stdout=PIPE,shell=True)
          output = p1.communicate()[0].decode("utf-8").lstrip().rstrip()
          logger.debug(output)
          debugDir="%s/debug/%s" % (logDir,str(int(time.time())))
#          debuglogfile="/%s/debug/%s_p%s.log" % (logDir,str(pid),str(int(time.time())))
          mycmd="mkdir %s;cp %s* %s/ " % (debugDir,logfile,debugDir)
          p1 = Popen([mycmd], stdout=PIPE,shell=True)
          output = p1.communicate()[0].decode("utf-8").lstrip().rstrip()
          logger.debug(output)
  
  if args['singleExecute']:
    runTask(logger)
  if args['test']:
    n=1000
    for i in range(n):
      logger.info(i)
      myTask=Task.objects.create(libName='misc',processName='test',objID=i)
      
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
