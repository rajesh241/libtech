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
from crawlSettings import nregaWebDir,nregaRawDataDir
from crawlFunctions import alterHTMLTables,writeFile
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable
from libtechFunctions import singleRowQuery,getFullFinYear
regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
regex1=re.compile(r'</td></font></td>',re.DOTALL)
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
    myURL = downloadMuster(pyCursor1,self.a)
    query = 'select musterNo,workName from musters where id=%d' % (self.a)
    pyCursor1.execute(query)
    row=pyCursor1.fetchone()
    return str(row[0])+"_"+str(self.a)+"_"+myURL

def downloadMuster(cur,mid):
  query="select fullBlockCode,panchayatCode,musterNo,workName,DATE_FORMAT(dateFrom,'%d/%m/%Y'),DATE_FORMAT(dateTo,'%d/%m/%Y'),workCode,finyear from musters where id="+str(mid)
  cur.execute(query)
  row=cur.fetchone()
  fullPanchayatCode=row[0]+row[1]
  fullBlockCode=row[0]
  panchayatCode=row[1]
  musterNo=str(row[2])
  workName=row[3].replace(" ","+")
  dateFrom=str(row[4])
  dateTo=str(row[5])
  workCode=row[6]
  fullFinYear=getFullFinYear(row[7]) 
  query="select crawlIP,stateName,rawDistrictName,rawBlockName,rawPanchayatName,stateShortCode,stateCode,districtCode,blockCode,panchayatName from panchayats where fullPanchayatCode='%s'" % (fullPanchayatCode)
  cur.execute(query)
  row=cur.fetchone()
  crawlIP=row[0]
  stateName=row[1]
  districtName=row[2]
  blockName=row[3]
  panchayatName=row[4] 
  stateShortCode=row[5]
  stateCode=row[6]
  districtCode=row[7]
  blockCode=row[8]
  panchayatNameAltered=row[9]

  musterURL="http://%s/netnrega/citizen_html/musternew.aspx?state_name=%s&district_name=%s&block_name=%s&panchayat_name=%s&workcode=%s&panchayat_code=%s&msrno=%s&finyear=%s&dtfrm=%s&dtto=%s&wn=%s&id=1" % (crawlIP,stateName.upper(),districtName.upper(),blockName.upper(),panchayatName,workCode,fullPanchayatCode,musterNo,fullFinYear,dateFrom,dateTo,workName)
  r=requests.get(musterURL)
  #Irrespective of result of download lets set downloadAttemptDate
  query="update musters set downloadAttemptDate=NOW() where id="+str(mid)
  cur.execute(query)

  mustersource=r.text
  myhtml=mustersource.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')

  myhtml=re.sub(regex,"",myhtml)
  myhtml=re.sub(regex1,"</font></td>",myhtml)

  jobcardPrefix="%s-%s-%s-%s" % (stateShortCode,districtCode,blockCode,panchayatCode)
  s=''
  if jobcardPrefix in myhtml:
    s="Muster Downloaded SuccessFully"
    title="Muster No : %s,  %s-%s-%s " % (str(musterNo),districtName,blockName,panchayatName)
    orightml=myhtml
    tableIDs=["ctl00_ContentPlaceHolder1_grdShowRecords"]
    myhtml=alterHTMLTables(myhtml,title,tableIDs)
    modifiedMusterFilePath=nregaWebDir.replace("stateName",stateName.upper()).replace("districtName",districtName.upper())
    fileName=modifiedMusterFilePath+blockName.upper()+"/MUSTERS/"+fullFinYear+"/"+musterNo+".html"
    fileName1=modifiedMusterFilePath+blockName.upper()+"/MUSTERS/"+fullFinYear+"/"+musterNo+"_orig.html"
    s+=fileName
    fileExists=0
    if (os.path.isfile(fileName)):
      fileExists=1
    #if fileExists == 0:
    writeFile(fileName,myhtml) 
    writeFile(fileName1,orightml) 
  htmlsoup=BeautifulSoup(myhtml,"lxml")
  return s+musterURL+jobcardPrefix

def main():
  regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
  args = argsFetch()
  finyear=args['finyear']
  if args['limit']:
    limit = int(args['limit'])
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
  maxProcess=1
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

