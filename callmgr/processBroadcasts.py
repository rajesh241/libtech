import MySQLdb
import datetime
import os
import sys

fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../includes/')
import libtechFunctions
import globalSettings
import settings
from settings import dbhost,dbuser,dbpasswd,sid,token
from libtechFunctions import gethtmlheader 
from libtechFunctions import gethtmlfooter 
from libtechFunctions import singleRowQuery,arrayToHTMLLine,writecsv 
from broadcastFunctions import scheduleGeneralBroadcastCall,getLocationQueryMatchString,getGroupQueryMatchString,gettringoaudio,getaudio
def main():
  todaydate=datetime.date.today().strftime("%d%B%Y")
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use libtech"
  cur.execute(query)
  query="select bid,type,minhour,maxhour,tfileid,fileid,groups,vendor,district,blocks,panchayats,priority,fileid2,template from broadcasts where error=0 and approved=1 and processed=0 and startDate <= CURDATE();"
  print query
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    bid=str(row[0])
    template=row[13]
    if((template == 'general') or  (template == 'feedback')):
      scheduleGeneralBroadcastCall(cur,bid)

      query="update broadcasts set processed=1 where bid="+bid
      cur.execute(query)
#   else:
#     query="update broadcasts set error=1 where bid="+bid
#     cur.execute(query)
if __name__ == '__main__':
  main()
