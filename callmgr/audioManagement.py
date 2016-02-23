from bs4 import BeautifulSoup

import time
import os
import sys
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../includes/')
import libtechFunctions

import sys
sys.path.insert(0, rootdir)

import wave
import contextlib
import math
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery
audioDir="/home/libtech/webroot/broadcasts/audio/"

def updateDurationPercentage(cur,logger):
  query="select cs.callid,b.totalDuration,cs.duration from callSummary cs,broadcasts b where cs.bid=b.bid and b.template='general' and b.durationError=0 and b.totalDuration!=0 and cs.status='success' and cs.durationPercentage=0 order by callid DESC "
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    callid=str(row[0])
    totalDuration=row[1]
    duration=row[2]
    logger.info("callid %s, totalDuration: %s duration: %s" % (callid,str(totalDuration),str(duration) ))
    if duration > totalDuration:
      durationPercentage=100
    else:
      durationPercentage=math.trunc(100*duration/totalDuration)
    query="update callSummary set durationPercentage=%s where callid=%s " % (str(durationPercentage),callid)
 #   logger.info(query)
    cur.execute(query)

def getAudioLength(cur,logger):
  query="select id,filename from audioLibrary where length=0"
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    rowid=str(row[0])
    filename=row[1]
    fname=audioDir+filename
    error=0
    try:
      with contextlib.closing(wave.open(fname,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        durationStr=str(math.trunc(duration))
    except:
      logger.info("ERROR ERROR: file ID %s filename %s Duration %s" % (rowid,filename,durationStr)) 
      durationStr='0'
      error=1
    logger.info("file ID %s filename %s Duration %s" % (rowid,filename,durationStr)) 
    query="update audioLibrary set length=%s,lengthError=%s where id=%s" % (durationStr,str(error),rowid)
    logger.info("Query "+query)
    cur.execute(query)
    
def getBroadcastDuration(cur,logger):
  query="select bid,fileid from broadcasts where template='general' and vendor != 'tringo'"
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    bid=str(row[0])
    fileids=row[1]
    logger.info("BID: %s File ID %s " % (bid,fileids))
    fileidArray=fileids.split(",")
    totalDuration=0
    error=0
    for fileid in fileidArray:
      logger.info("File id %s" % str(fileid))
      query="select length from audioLibrary where id=%s" % str(fileid)
      cur.execute(query)
      if cur.rowcount == 1:
        row=cur.fetchone()
        totalDuration+=row[0]
      else:
        error=1
    logger.info("TotalDuration %s" % str(totalDuration))
    query="update broadcasts set totalDuration=%s,durationError=%s where bid=%s" % (str(totalDuration),str(error),bid)
    cur.execute(query)

def uploadAudioToAwaazDe(cur,logger):
  from awaazde import awaazdeUpload
  from datetime import datetime, timedelta
  from time import strftime
  query="select id,filename,ts,awaazdeUploadDate from audioLibrary where awaazdeUploadComplete=0 and ts > '2016-02-21'" # and TIMESTAMPDIFF(MINUTE, awaazdeUploadComplete, now()) < 60"
  cur.execute(query)
  results = cur.fetchall()
  for (rowid, filename, timestamp, uploadDate)  in results:
    if uploadDate and uploadDate > datetime.now() - timedelta(minutes=60):
      continue

    logger.info("rowid[%s], filename[%s], timestamp[%s], uploadDate[%s]" % (rowid, filename, timestamp, uploadDate))
    awaazdeUpload(filename)
    query = 'update audioLibrary set awaazdeUploadDate="%s", awaazdeUploadComplete=1 where id="%s"' % (strftime('%Y-%m-%d %H:%M:%S'), rowid)
    cur.execute(query)

    
def main():
  logger = loggerFetch()

  db = dbInitialize(db="libtech", charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query) 

  getAudioLength(cur,logger)
  getBroadcastDuration(cur,logger)
  updateDurationPercentage(cur,logger)
  uploadAudioToAwaazDe(cur, logger)
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  exit(0)

if __name__ == '__main__':
  main()
