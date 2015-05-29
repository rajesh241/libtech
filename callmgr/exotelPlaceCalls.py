import MySQLdb
import datetime
import os
from settings import dbhost,dbuser,dbpasswd,sid,token
import requests
import xml.etree.ElementTree as ET

def connect_customer(sid, token,
                     customer_no, customField,exotel_no="08033545179", callerid="08033545179", url="http://my.exotel.in/exoml/start/44458",
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
  query="select c.id,c.phone from callQueue c,broadcasts b where c.vendor='exotel' and c.minhour <= "+curhour+" AND c.maxhour > "+curhour+" and b.endDate >= CURDATE() and c.inprogress=0 order by c.minhour limit 1"
  cur.execute(query)
  results = cur.fetchall()
  print "curhour is "+curhour
  for row in results:
    callid=str(row[0])
    phone=row[1]
    print callid+"  "+phone
    r = connect_customer(
        sid, token,
        customer_no=phone,
        customField=callid

        )
    print r.status_code
    if (r.status_code == 200):
      print r.content
      root = ET.fromstring(r.content)
      for Call in root.findall('Call'):
        sid1 = Call.find('Sid').text
      query="update callQueue set sid='"+sid1+"',callRequestTime=NOW(),inprogress=1 where id="+callid
      print query
      cur.execute(query)




if __name__ == '__main__':
  main()
