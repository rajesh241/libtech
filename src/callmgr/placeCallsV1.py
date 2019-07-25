from bs4 import BeautifulSoup
import datetime
import os
import requests
import xml.etree.ElementTree as ET
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../includes/')

from wrappers.logger import loggerFetch
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery
from settings import sid,token
from globalSettings import maxTringoCallQueue,maxExotelCallQueue
def connect_customer(sid, token,
                     customer_no, customField,exotel_no="02233814264", callerid="02233814264", url="http://my.exotel.in/exoml/start/44458",
                     timelimit=None, timeout=None, calltype="trans",
                     callback_url=None):
    return requests.post('https://twilix.exotel.in/v1/Accounts/{sid}/Calls/connect'.format(sid=sid),
        auth=(sid, token),
        data={
            'From': customer_no,
            'To': exotel_no,
            'CallerId': callerid,
            'Url': url,
            'TimeLimit': timelimit,
            'TimeOut': timeout,
            'CallType': calltype,
            'CustomField': customField,
            'StatusCallback': callback_url
        })


def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Jobcard script for crawling, downloading & parsing')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-t', '--timeout', help='Time to wait before a page loads', required=False)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-u', '--url', help='Specify the url to crawl', required=False)
#  parser.add_argument('-f', '--filename', help='Specify the wave file to upload', required=True)
  parser.add_argument('-d', '--directory', help='Specify directory to download html file to', required=False)

  args = vars(parser.parse_args())
  return args

def getTringoAudioArray(cur,audio,logger):
  logger.info("Getting Tringo Audio for %s " % audio)
  tringoAudioList=[]
  i=0
# while i<20:
#  i=i+1
#  tringoAudioList.append(27503)
  
  audioList=audio.split(",")
  i=0
  error=0
  for audioName in audioList:
    query="select tringoFileID from audioLibrary where filename='%s'" % (audioName)
    logger.info("QUery %s " % query)
    cur.execute(query)
    if cur.rowcount > 0:
      audioRow=cur.fetchone()
      tringoFileID = audioRow[0]
      tringoAudioList.append(tringoFileID)
    else:
      error=1
  if error==0:
    while len(tringoAudioList) < 20:
      tringoAudioList.append('27503')
  i=0
  tringoAudioString=''
  for tringoAudio in tringoAudioList: 
    i=i+1
    mystr="fileid"+str(i)+"="+tringoAudio+"&"
    tringoAudioString+=mystr
  logger.info("Now the audio List contains %s " % (str(len(tringoAudioList))))
  logger.info("Now the audio List contains %s " %  ''.join(tringoAudioList) )
  logger.info("Now the audio List contains %s " %  tringoAudioString )
  return error,tringoAudioString

def main():
  now = datetime.datetime.now()
  curhour = str(now.hour)
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  db = dbInitialize(db="libtech", charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  
  query="select count(*) from callQueue where inprogress=1 and curVendor='exotel'"
  curExotelQueue=singleRowQuery(cur,query)
  logger.info("Current Exotel CallQueue %s" % (curExotelQueue))
  if(curExotelQueue < maxExotelCallQueue):
   # logger.info("No more calls will be placed through Exotel")
    query="select c.callid,c.phone,c.exophone,c.template from callQueue c,broadcasts b,addressbook a where c.phone=a.phone and a.dnd='no' and b.bid=c.bid and (c.retry=0 or (TIMESTAMPDIFF(MINUTE,c.callRequestTime,NOW()) >= b.backoff ) ) and c.minhour <= "+curhour+" AND c.maxhour > "+curhour+" and b.endDate >= CURDATE() and c.inprogress=0 and c.preference > 20 order by c.preference DESC,isTest DESC,c.retry limit 50"
    logger.info("Query : %s" % query)
    cur.execute(query)
    results = cur.fetchall()
    for row in results:
      callid=str(row[0])
      phone=row[1]
      exophone=str(row[2])
      template=str(row[3])
      exotelURL='http://my.exotel.in/exoml/start/44458'
      if (template == 'feedback'):
        exotelURL='http://my.exotel.in/exoml/start/50053'
      elif (template == 'wageBroadcast'):
        exotelURL='http://my.exotel.in/exoml/start/51210'
      elif (template == 'biharVoiceMail'):
        exotelURL='http://my.exotel.in/exoml/start/42212'
      elif (template == 'ghattuFeedback'):
        exotelURL='http://my.exotel.in/exoml/start/62882'
      elif (template == 'rscdFeedback'):
        exotelURL='http://my.exotel.in/exoml/start/107221'
      elif (template == 'voiceMail'):
        exotelURL='http://my.exotel.in/exoml/start/117346'

      logger.info("Placing Call callid: %s phone: %s " % (callid,phone))
      r = connect_customer(
          sid, token,
          exotel_no=exophone,
          url=exotelURL,
          callerid=exophone, 
          customer_no=phone,
          customField=callid
   
          )
      #print r.status_code
     # print r.content
      if (r.status_code == 403):
        root = ET.fromstring(r.content)
        for restException in root.findall('RestException'):
          message1 = restException.find('Message').text
        if 'TRAI NDNC' in message1:
          logger.info("This seems to be the DND number")
          query="update addressbook set dnd='yes' where phone='%s' " % phone
          cur.execute(query)
      if (r.status_code == 200):
        #print r.content
        root = ET.fromstring(r.content)
        for Call in root.findall('Call'):
          sid1 = Call.find('Sid').text
          logger.info("Call Placed Successful with SID : %s" % sid1)
        query="update callQueue set sid='"+sid1+"',callRequestTime=NOW(),curVendor='exotel',inprogress=1 where callid="+callid
        #print query
        cur.execute(query)
  
  query="select count(*) from callQueue where inprogress=1 and curVendor='tringo'"
  curTringoQueue=singleRowQuery(cur,query)
  logger.info("Current Tringo CallQueue %s" % (curTringoQueue))
  if(curTringoQueue < maxTringoCallQueue):
    query="select c.callid,c.phone,c.exophone,c.audio from callQueue c,broadcasts b,addressbook a where c.phone=a.phone and a.dnd='yes' and c.template='general' and b.bid=c.bid  and c.minhour <= "+curhour+" AND c.maxhour > "+curhour+" and b.endDate >= CURDATE() and c.inprogress=0 and c.preference > 20 order by c.preference DESC,isTest DESC,c.retry limit 1"
    logger.info("Query : %s" % query)
    cur.execute(query)
    results = cur.fetchall()
    for row in results:
      callid=str(row[0])
      phone=row[1]
      exophone=str(row[2])
      audio=str(row[3])
      tringoError,tringoaudio=getTringoAudioArray(cur,audio,logger)
      if tringoError == 0:
        tringourl='http://hostedivr.in/netobd/NewCall_Schedule.php?uid=523&pwd=golani123&pno=%s&%sivrid=2' % (phone,tringoaudio)
        logger.info("Tringo URL %s" % tringourl)
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors

if __name__ == '__main__':
  main()
