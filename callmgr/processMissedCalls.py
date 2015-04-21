import MySQLdb
import datetime
import os
import math
import time

def main():
  ts=math.trunc(time.time())
  db = MySQLdb.connect(host="localhost", user="root", passwd="ccmpProject**", db="libtech",charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  query="select id,phone,ctime from ghattuMissedCalls where processed=0 "
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    missedCallID=row[0]
    phone=row[1]
    ctime=row[2]
    query="update ghattuMissedCalls set processed=1 where id="+str(missedCallID)
    cur.execute(query)
    query="use mahabubnagar"
    cur.execute(query)
    query="select jobcard from jobcardDetails where phone='"+phone+"' limit 1"
    cur.execute(query)
    jobcard=0
    if(cur.rowcount == 1):
      row1=cur.fetchone()
      jobcard=row1[0]
    query="use libtech"
    cur.execute(query)
    query="insert into ghattuMissedCallsLog (missedCallID,phone,ctime,ts,jobcard,htmlgen,currentStep) values ("+str(missedCallID)+",'"+phone+"','"+str(ctime)+"',"+str(ts)+",'"+str(jobcard)+"',0,'Call Pending');"
    print query
    cur.execute(query)

if __name__ == '__main__':
  main()
