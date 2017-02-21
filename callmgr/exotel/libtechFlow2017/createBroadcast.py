#! /usr/bin/env python

import cgi
import cgitb; cgitb.enable() # Optional; for debugging only

import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(os.path.dirname(os.path.dirname(dirname)))

import sys
sys.path.insert(0, rootdir)
import datetime

from wrappers.db import dbInitialize,dbFinalize


def main():
  print 'Content-type: text/html'
  print 
  db = dbInitialize(db="libtech")
  cur = db.cursor()
  form = cgi.FieldStorage()
  exophone=form['To'].value
  sid = form['CallSid'].value
  digits = form['digits'].value
  query="select region from regions where exophone='%s' " % exophone
  cur.execute(query)
  row=cur.fetchone()
  region=row[0]
  todayDate=datetime.datetime.now().strftime('%d%b%Y')
  bname="%s_%s" % (region,todayDate)
  query="select groupID from ivrGroupInfo where region='%s' and groupCode=%s " % (region,str(digits))
  cur.execute(query)
  if cur.rowcount > 0:
    row=cur.fetchone()
    groupID=str(row[0])
    query="select filename from exotelRecordings where sid='%s' order by id DESC limit 1" % sid
    cur.execute(query)
    row=cur.fetchone()
    filename=row[0]
    query="select id from audioLibrary where filename='%s' " % filename
    cur.execute(query)
    row=cur.fetchone()
    fileid=str(row[0]) 
    query="insert into broadcasts (fileid2,tfileid,approved,priority,name,vendor,type,region,template,startDate,endDate,minhour,maxhour,fileid,groups) values ('','',1,1,'%s','any','group','%s','general',NOW(),'2020-01-01',8,20,%s,%s)" % (bname,region,str(fileid),str(groupID))
  with open('/tmp/yuyyyy.txt', 'w') as outfile:
    outfile.write(str(form)+query)
  cur.execute(query)
 
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
 
if __name__ == '__main__':
  main()
