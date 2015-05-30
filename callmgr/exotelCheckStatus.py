import MySQLdb
import datetime
import os
from settings import dbhost,dbuser,dbpasswd,sid,token
import requests
import xml.etree.ElementTree as ET
#callstatuscode="""
#The "Status" parameter can take one of the following values: 
#       - queued
#       - in-progress
#       - completed
#       - failed
#       - busy
#       - no-answer"""
def main():
  todaydate=datetime.date.today().strftime("%d%B%Y")
  now = datetime.datetime.now()
  curhour = str(now.hour)
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use libtech"
  cur.execute(query)
  query="select id,sid,bid,callRequestTime,phone,retry,audio from callQueue where vendor='exotel' and inprogress=1"
  cur.execute(query)
  results = cur.fetchall()
  print "curhour is "+curhour
  for row in results:
    callid=str(row[0])
    callsid=row[1]
    bid=str(row[2])
    callRequestTime=str(row[3])
    phone=str(row[4])
    retry=str(row[5]+1)
    audio=row[6]
    url="https://"+sid+":"+token+"@twilix.exotel.in/v1/Accounts/"+sid+"/Calls/"+callsid
    r = requests.get(url)
    print r.content
    root = ET.fromstring(r.content)
    for Call in root.findall('Call'):
      callsid = Call.find('Sid').text
      status = Call.find('Status').text
      callStartTime = Call.find('StartTime').text
      duration = Call.find('Duration').text
    if duration is None:
      duration=0
    print status
    callinprogress=1
    query="insert into callLogs (vendor,bid,sid,phone,retry,callRequestTime,callStartTime,duration,status,audio) values ('exotel',"+bid+",'"+callsid+"','"+phone+"',"+retry+",'"+callRequestTime+"','"+callStartTime+"',"+str(duration)+",'"+status+"','"+audio+"');"
    cur.execute(query)
    print query
    if(status == "completed"):
      callinprogress=0
      success=1
      print "The Call has been completed Successfully"
    elif(status == "busy" or status=="no-answer" or status=="failed"):
      callinprogress=0
      print "The Call has failed"
    if(callinprogress == 0):
      query="insert into callLogs (vendor,bid,sid,phone,retry,callRequestTime,callStartTime,duration,status,audio) values ('exotel',"+bid+",'"+callsid+"','"+phone+"',"+retry+",'"+callRequestTime+"','"+callStartTime+"',"+str(duration)+",'"+status+"','"+audio+"');"
      cur.execute(query)
      print query


if __name__ == '__main__':
  main()
