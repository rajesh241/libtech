import MySQLdb
import datetime
import os
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../includes/')
from settings import dbhost,dbuser,dbpasswd,sid,token
import requests
import xml.etree.ElementTree as ET

def singleRowQuery(cur,query):
  cur.execute(query)
  result=cur.fetchone()
  return result[0]


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

def handleDNDError(cur,callid):
##First we need to find out if any other vendor other than exotel can be used for this call
  query="select bid from callQueue where callid="+str(callid)
  bid=singleRowQuery(cur,query)
  query="select vendor from broadcasts where bid="+str(bid)
  vendor=singleRowQuery(cur,query)
  if vendor=='any':
    query="update callQueue set vendor='tringo',preference=0 where callid="+callid
    print query
    cur.execute(query)
  else:
    query="delete from callQueue where callid="+callid
    cur.execute(query)
    query="update callSummary set status='error' where callid="+callid 
    cur.execute(query)
  
def main():
  maxTringoCallQueue=32 #This is the maximum number of calls that can be queued with Tringo
  maxExotelCallQueue=64 #This is the maximum number of calls that can be queued with exotel
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
  query="select count(*) from callQueue where inprogress=1 and curVendor='exotel'"
  curQueue=singleRowQuery(cur,query)
  print "Current Queued Calls in Tringo is "+str(curQueue)
  if(curQueue < maxExotelCallQueue):
    query="select c.callid,c.phone,c.exophone,c.template from callQueue c,broadcasts b where b.bid=c.bid and (c.vendor='exotel' or c.vendor='any') and c.minhour <= "+curhour+" AND c.maxhour > "+curhour+" and b.endDate >= CURDATE() and c.inprogress=0 and c.preference > 20 order by c.preference DESC,isTest DESC,c.retry limit 1"
    print query
    cur.execute(query)
    results = cur.fetchall()
    print "curhour is "+curhour
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
      print callid+"  "+phone
      r = connect_customer(
          sid, token,
          exotel_no=exophone,
          url=exotelURL,
          callerid=exophone, 
          customer_no=phone,
          customField=callid
   
          )
      print r.status_code
      print r.content
      if (r.status_code == 403):
        root = ET.fromstring(r.content)
        for restException in root.findall('RestException'):
          message1 = restException.find('Message').text
        print message1
        if 'TRAI NDNC' in message1:
          print "This seems to be the DND number"
          handleDNDError(cur,callid)
      if (r.status_code == 200):
        #print r.content
        root = ET.fromstring(r.content)
        for Call in root.findall('Call'):
          sid1 = Call.find('Sid').text
        query="update callQueue set sid='"+sid1+"',callRequestTime=NOW(),curVendor='exotel',inprogress=1 where callid="+callid
        print query
        cur.execute(query)

  #Here below we will write the code to place calls through tringo
  query="select count(*) from callQueue where inprogress=1 and curVendor='tringo'"
  curQueue=singleRowQuery(cur,query)
  print "Current Queued Calls in Tringo is "+str(curQueue)
  if(curQueue < maxTringoCallQueue):
    query="select c.callid,c.phone,c.tringoaudio from callQueue c,broadcasts b where c.bid=b.bid and (c.vendor='tringo' or c.vendor='any') and c.minhour <= "+curhour+" AND c.maxhour > "+curhour+" and b.endDate >= CURDATE() and c.inprogress=0 and c.preference > 20 order by c.preference DESC,isTest DESC,c.retry,c.vendor DESC limit 1"
    print query
    cur.execute(query)
    results = cur.fetchall()
    for row in results:
      callid=str(row[0])
      phone=row[1]
      audio=row[2]
      print callid+"  "+phone
      tringurl='http://hostedivr.in/netobd/NewCall_Schedule.php?uid=523&pwd=golani123&pno=%s%s&ivrid=2' % (phone,audio)
      print tringurl
      r = requests.get(tringurl)
      tringsid=r.content
      sid1=tringsid.strip()
      print "Tringo SID is "+sid1
      if (sid1.isdigit()):
        print "sid1 contains only digits"
        query="update callQueue set sid='"+sid1+"',callRequestTime=NOW(),curVendor='tringo',inprogress=1 where callid="+callid
        print query
        cur.execute(query)
      
if __name__ == '__main__':
  main()