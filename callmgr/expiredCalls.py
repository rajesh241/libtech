import MySQLdb
import datetime
import os
import time
from settings import dbhost,dbuser,dbpasswd,sid,token


def main():
  finalCallStatus='expired'
  duration=0
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use libtech"
  cur.execute(query)
  query="select c.id,c.vendor,c.bid,c.phone,c.retry from callQueue c,broadcasts b  where b.bid=c.bid and b.endDate < CURDATE() and c.inprogress=0 "
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    callid=row[0] 
    vendor=row[1]
    bid=str(row[2])
    phone=row[3]
    retry=row[4]
    query="update callStatus set status='"+finalCallStatus+"',attempts="+str(retry)+",vendor='"+vendor+"',duration="+str(duration)+" where  bid="+bid+" and phone='"+phone+"';"
    print query
    cur.execute(query)
    query="delete from callQueue where id="+str(callid)
    print query
    cur.execute(query)

if __name__ == '__main__':
  main()
