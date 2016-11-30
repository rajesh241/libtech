from bs4 import BeautifulSoup
import multiprocessing, time
import requests
import MySQLdb
import os
import time
import re
import sys
from MySQLdb import OperationalError
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
#sys.path.insert(0, rootdir)
import datetime
from wrappers.logger import loggerFetch
from wrappers.db import dbInitialize,dbFinalize
from crawlSettings import nregaDB 
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable
from libtechFunctions import singleRowQuery,getFullFinYear,writeFile
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing musters')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-f', '--finyear', help='Download musters for that finyear', required=True)
  parser.add_argument('-d', '--district', help='District for which you need to Download', required=False)
  parser.add_argument('-b', '--blockCode', help='BlockCode for  which you need to Download', required=False)
  parser.add_argument('-p', '--panchayatCode', help='panchayatCode for  which you need to Download', required=False)
  parser.add_argument('-limit', '--limit', help='District for which you need to Download', required=False)

  args = vars(parser.parse_args())
  return args

class musterProcess(multiprocessing.Process):
    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.pyConn = dbInitialize(db=nregaDB, charset="utf8")  # The rest is updated automatically in the function
        #self.pyConn.set_isolation_level(0)
        self.pyConn.autocommit(True)


    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                logger.info('Tasks Complete')
                self.task_queue.task_done()
                dbFinalize(self.pyConn) # Make sure you put this if there are other exit paths or errors
                break            
            answer = next_task(connection=self.pyConn)
            self.task_queue.task_done()
            self.result_queue.put(answer)
        return

class Task(object):
  def __init__(self, a):
    self.a = a
  def __call__(self,connection=None):
    pyConn = connection
    pyCursor1 = pyConn.cursor()
    query = 'select musterNo,workName from musters where id=%d' % (self.a)
    pyCursor1.execute(query)
    row=pyCursor1.fetchone()
    return str(row[0])+"_"+str(self.a)


def main():
  regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
  args = argsFetch()
  finyear=args['finyear']
  if args['limit']:
    limit = args['limit']
  else:
    limit =500
  fullfinyear=getFullFinYear(finyear)
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("BEGIN PROCESSING...")


  db = dbInitialize(db=nregaDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  tasks = multiprocessing.JoinableQueue()
  results = multiprocessing.Queue()
  maxProcess=5
  myProcesses=[musterProcess(tasks, results) for i in range(maxProcess)]
  for eachProcess in myProcesses:
    eachProcess.start()

  query="select id from musters limit %s" % str(limit)
  cur.execute(query)
  results1=cur.fetchall()
  for row in results1:
    musterID=row[0]
    tasks.put(Task(musterID))  
  
  for i in range(maxProcess):
    tasks.put(None)

  while limit:
    result = results.get()
    logger.info(result)
    limit -= 1


  dbFinalize(db) # Make sure you put this if there are other exit paths or errors

if __name__ == '__main__':
  main()

