from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
import time
import re
import sys
from MySQLdb import OperationalError
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../includes/')
sys.path.insert(0, fileDir+'/../')
#sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery,getjcNumber,getFullFinYear,writeFile,writeFile3
sys.path.insert(0, fileDir+'/../crawlDistricts/')
from globalSettings import genericVoiceMailAudioDir
from settings import sid,token
import xml.etree.ElementTree as ET
def exotelCallStatusVoiceMail (sid,token,callsid):
  url="https://"+sid+":"+token+"@twilix.exotel.in/v1/Accounts/"+sid+"/Calls/"+callsid
  r = requests.get(url)
  #print "Request Status"+str(r.status_code)
  callinprogress=1
  if (r.status_code == 200):
     #print r.content
     root = ET.fromstring(r.content)
     for Call in root.findall('Call'):
       recordingURL = Call.find('RecordingUrl').text
       return recordingURL
  else:
    return "error"


def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script to Post Process Generic Broadcasts')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-bid', '--broadcastID', help='Broadcast ID ', required=False)
  parser.add_argument('-limit', '--limit', help='Limit the number of entries that need to be processed', required=False)
  args = vars(parser.parse_args())
  return args
  
def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  broadcastFilter=''
  logger.info("BEGIN PROCESSING...")
  if args['broadcastID']:
    broadcastFilter=' and bid=%s ' % args['broadcastID']
  
  db = dbInitialize(db="libtech", charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)

  query="select bid,completed from broadcasts where  template='voiceMail' and isPostProcessed=0 %s" % broadcastFilter
  cur.execute(query)
  results1=cur.fetchall()
  for row1 in results1:
    bid=str(row1[0])
    isComplete=row1[1]
    logger.info("Processed Broadcasts bid : %s " % bid)
    query="select callid,sid,phone,attempts,duration,status,callStartTime,TIMESTAMPDIFF(HOUR, callStartTime, now())  from callSummary where bid=%s " % bid
    logger.info(query)
    cur.execute(query)
    results = cur.fetchall()
    csvtext="callid,callsid,phone,attempts,duration,status,callStartTime,audioURL\n"
    filepath=genericVoiceMailAudioDir+"/"+bid+"/"
    for row in results:
      callid=str(row[0])
      callsid=row[1]
      phone=row[2]
      attempts=str(row[3])
      duration=str(row[4])
      status=row[5]
      callStartTime=str(row[6])
      timediff=str(row[7])
      #print phone+status+timediff
      audioURL="None"
      if status=='success':
        recordingURL=exotelCallStatusVoiceMail(sid,token,callsid) 
        #print recordingURL
        if recordingURL is None:
          recordingURL="error"
        logger.info("Recording URL %s " % recordingURL)
        if recordingURL != "error":
          #print recordingURL 
          r=requests.get(recordingURL)
          audiofilename=filepath+phone+".mp3"
          writeFile3(audiofilename,r.content)
          f = open(audiofilename, 'w')
          f.write(r.content)
          audioURL="http://callmgr.libtech.info/open/audio/genericVoiceMail/"+bid+"/"+phone+".mp3"
          #print audioURL
      csvtext+="%s,%s,%s,%s,%s,%s,%s,%s\n" %(callid,callsid,phone,attempts,duration,status,callStartTime,audioURL)
      #print csvrow 
      #print phone+status+audioURL
    print csvtext
    csvfilename=filepath+bid+".csv"
    writeFile3(csvfilename,csvtext)
    # Make broadcast ready for new calls
    if isComplete==1:
      query="update broadcasts set isPostProcessed=1 where bid=%s " % bid
  #    cur.execute(query)




  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
