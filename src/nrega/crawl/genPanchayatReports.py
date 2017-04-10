from bs4 import BeautifulSoup
import multiprocessing, time
import requests
import MySQLdb
import os
import os.path
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
from crawlSettings import nregaWebDir,nregaRawDataDir,nregaWebDirRoot
from crawlFunctions import  tabletUIQueryToHTMLTable,htmlWrapperLocal,tabletUIReportTable
from crawlFunctions import alterHTMLTables,writeFile,getjcNumber,NICToSQLDate,getFullFinYear
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing musters')
  args = vars(parser.parse_args())
  return args
 

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))

  db = dbInitialize(db=nregaDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)


  dbFinalize(db) # Make sure you put this if there are other exit paths or errors

if __name__ == '__main__':
  main()
