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
#callstatuscode="""
#The "status" parameter from exotelcan take one of the following values: 
#       - queued
#       - in-progress
#       - completed
#       - failed
#       - busy
#       - no-answer"""


#Our Status codes
#vendorstatus is the raw status as got from vendor
#callstatus   has values success,fail,error
#finalCallStatus has values success,maxRetryFailed,expired

def tringoCallStatus (sid,token,callsid):
  url='http://www.hostedivr.in/netobd/fetchCallRecord.php?uid=523&pwd=golani123&callreqid='+callsid;
  print url
  r = requests.get(url)
  tringstatus=r.content
  print tringstatus
  statusArray=tringstatus.split('|')
  lenArray=len(statusArray)
  callinprogress=1
  callpass=0
  callfail=0
  duration=0
  price=0
  callStartTime=''
  if (lenArray == 9):
    print "Length of Status is "+str(lenArray)
    status=statusArray[5]
    callStartTime=statusArray[2]
    print callStartTime+status
    if(status == "COMPLETE"):
      callpass=1
      callinprogress=0
      callStartTime=statusArray[3]
      callEndTime=statusArray[4]
      callStartTimeEpoch=time.mktime(datetime.datetime.strptime(callStartTime, "%Y-%m-%d %H:%M:%S").timetuple())
      callEndTimeEpoch=time.mktime(datetime.datetime.strptime(callEndTime, "%Y-%m-%d %H:%M:%S").timetuple())
      duration=int(callEndTimeEpoch)-int(callStartTimeEpoch)
      #print str(callStartTimeEpoch)+"\n"
      #print str(callEndTimeEpoch)+"\n"
      price=statusArray[6]
       
      price = float(price.strip(' "'))

    if(status == "INCOMPLETE"):
      callfail=1
      callinprogress=0
      
    cost=price*100   # Store in paise
    print( "Cost[%s]" % cost)

    return callinprogress,callpass,callfail,callStartTime,duration,cost,status

def exotelCallStatus (sid,token,callsid):
  url="https://"+sid+":"+token+"@twilix.exotel.in/v1/Accounts/"+sid+"/Calls/"+callsid
  r = requests.get(url)
  print "Request Status"+str(r.status_code)
  callinprogress=1
  if (r.status_code == 200):
     print r.content
     callpass=0
     callfail=0
     root = ET.fromstring(r.content)
     for Call in root.findall('Call'):
       callsid = Call.find('Sid').text
       status = Call.find('Status').text
       callStartTime = Call.find('StartTime').text
       duration = Call.find('Duration').text
       price = Call.find('Price').text
         
     if(status == "completed"):
       callinprogress=0
       callpass=1
       print "The Call has been completed Successfully"
       
       if (duration is None) or (price is None):
         duration=0
         callinprogress=1 #Make call in progress1 if the duration field is not updated. That means the duration field will get updated in sometime
     elif(status == "busy" or status=="no-answer" or status=="failed"):
       duration=0
       callinprogress=0
       callfail=1
       print "The Call has failed"

     if price == None:
       price="0"

     price = float(price.strip(' "'))  
     cost=price*100   # Store in paise
     print("Cost[%s]" % cost)
     
  return callinprogress,callpass,callfail,callStartTime,duration,cost,status


def main():
#Setting some Default Values
  minduration = 10
  maxretry=10

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
  query="select id,sid,bid,callRequestTime,phone,retry,audio,curVendor,tringoaudio,isTest,TIMESTAMPDIFF(HOUR, callRequestTime, now())  from callQueue where inprogress=1 "
  cur.execute(query)
  results = cur.fetchall()
  print "curhour is "+curhour
  for row in results:
    durationpass=0
    isMaxRetry=0
    callid=str(row[0])
    callsid=row[1]
    bid=str(row[2])
    callRequestTime=str(row[3])
    phone=str(row[4])
    retry=row[5]+1
    audio=row[6]
    vendor=row[7]
    tringoaudio=row[8]
    isTest=row[9]
    timeDiff=row[10]
    if(vendor == 'exotel'):
      callinprogress,callpass,callfail,callStartTime,duration,cost,vendorCallStatus = exotelCallStatus(sid,token,callsid)
    elif(vendor == 'tringo'):
      callinprogress,callpass,callfail,callStartTime,duration,cost,vendorCallStatus = tringoCallStatus(sid,token,callsid)
    #Here we need to put additional check to see if the call has errred or not. If the difference between the callRequest time and now() is created that 48 hours then we shall mark the calls as errors 
    callError=0
    if((timeDiff > 8) and (callinprogress == 1)):
      callinprogress=0
      callError=1
      duration=0
    finalCallSuccess=0
    finalCallmaxRetryFail=0
    finalCallExpired=0
    print "status received from exotel is "+vendorCallStatus
    print "Duration of the call is "+str(duration)
    print "Cost of the call is " + str(cost)
    print "call pass "+str(callpass)+"callfail ="+str(callfail)
    ###Now we have all the variables to implement our logic
    if(callinprogress == 0):
      if(retry >= maxretry):
        print "Max Retry is 1\n"
        isMaxRetry=1
      if((callpass == 1) and (int(duration) > minduration)):
        print "Duration Pass is 1\n"
        durationpass =1
      if( (durationpass == 1) or (isMaxRetry == 1)):
        #We need to remove this entry from callQueue
        query="delete from callQueue where id="+callid
        print query
        cur.execute(query)
        if(durationpass ==1):
          curCallStatus = "pass"
          finalCallSuccess=1
          finalCallStatus='success'
        else:
          curCallStatus = "fail"
          finalCallmaxRetryFail=1
          finalCallStatus='failMaxRetry'
        query="update callStatus set status='"+finalCallStatus+"',attempts="+str(retry)+",vendor='"+vendor+"',duration="+str(duration)+",callStartTime='"+callStartTime+"' where  bid="+bid+" and phone='"+phone+"';"
        print query
        if(isTest == 0):
          cur.execute(query)
      else:
      #We need to update callQueue with new retry count and inprogress=0
        query="update callQueue set curVendor='',sid='',retry="+str(retry)+",inprogress=0,preference=0 where id="+callid
        print query
        cur.execute(query)
        curCallStatus = "fail"
        if(callError ==1):
          curCallStatus='error'
      if(vendor == 'tringo'):
        audio=tringoaudio
      query="insert into callLogs (vendor,bid,sid,phone,retry,callRequestTime,callStartTime,duration,cost,status,audio,vendorCallStatus) values ('"+vendor+"',"+bid+",'"+callsid+"','"+phone+"',"+str(retry)+",'"+callRequestTime+"','"+callStartTime+"',"+str(duration)+","+str(cost)+",'"+curCallStatus+"','"+audio+"','"+vendorCallStatus+"');"
      print query
      cur.execute(query)
        
if __name__ == '__main__':
  main()
