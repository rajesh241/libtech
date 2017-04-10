
import MySQLdb
import datetime
import os
import sys
import time
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../includes/')
from settings import dbhost,dbuser,dbpasswd,sid,token
import requests
import xml.etree.ElementTree as ET

from globalSettings import datadir,nregaDataDir,biharAudioDir

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

def main():
#Setting some Default Values
  yesterday=datetime.date.fromordinal(datetime.date.today().toordinal()-1)
  todaydate=datetime.date.today().strftime("%d%B%Y")
  todaydate1=datetime.date.today().strftime("%Y-%m-%d")
  todaydate=yesterday.strftime("%d%B%Y")
  yesterdayYMD=yesterday.strftime("%Y-%m-%d")
  print todaydate
  biharAudioPath=biharAudioDir+"/"+todaydate+"/"
  csvfilename=biharAudioPath+"/"+todaydate+".csv"
  if not os.path.exists(os.path.dirname(csvfilename)):
    os.makedirs(os.path.dirname(csvfilename))
  now = datetime.datetime.now()
  curhour = str(now.hour)
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use libtech"
  cur.execute(query)
  
  query="select callid,sid,phone,attempts,duration,status,callStartTime,TIMESTAMPDIFF(HOUR, callStartTime, now())  from callSummary where bid=1503 and callRequestTime like '%"+yesterdayYMD+"%' " 
  print query
#  query="select callid,sid,phone,attempts,duration,status,callStartTime,TIMESTAMPDIFF(HOUR, callStartTime, now())  from callSummary where bid=1503 and callid < 543658 order by callid DESC limit 6 "
  cur.execute(query)
  results = cur.fetchall()
  print "curhour is "+curhour
  csvtext="callid,callsid,phone,attempts,duration,status,callStartTime,audioURL\n"
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
      if recordingURL != "error":
        #print recordingURL 
        r=requests.get(recordingURL)
        audiofilename=biharAudioPath+phone+".mp3"
        f = open(audiofilename, 'w')
        f.write(r.content)
        audioURL="http://callmgr.libtech.info/open/audio/biharAudio/"+todaydate+"/"+phone+".mp3"
        #print audioURL
    csvtext+="%s,%s,%s,%s,%s,%s,%s,%s\n" %(callid,callsid,phone,attempts,duration,status,callStartTime,audioURL)
    #print csvrow 
    #print phone+status+audioURL
  print csvtext
  csvfilename=biharAudioPath+"/"+todaydate+".csv"
  f = open(csvfilename, 'w')
  f.write(csvtext)
  # Make broadcast ready for new calls
  query="update broadcasts set endDate='%s',processed=0 where bid=1503 " % todaydate1 
  cur.execute(query)
if __name__ == '__main__':
  main()
