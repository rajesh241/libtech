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
  query="select region from regions where exophone='%s' " % exophone
  cur.execute(query)
  row=cur.fetchone()
  region=row[0]
  with open('/tmp/abcd10.txt', 'w') as outfile:
    outfile.write(str(form)+region)
  if region == 'jsk':
    with open('/tmp/abcd2.txt', 'w') as outfile:
      outfile.write(str(form))
    digits=1
  elif region == "msk" :
    digits=1
  else:
    digits = form['digits'].value
  s=''
  s+="region - %s " % region
  todayDate=datetime.datetime.now().strftime('%d%b%Y')
  bname="%s_%s" % (region,todayDate)
  query="select groupID from ivrGroupInfo where region='%s' and groupCode=%s " % (region,str(digits))
  s+=query
  with open('/tmp/zzzz.txt','w') as f:
    f.write(s)
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
    approved=0
    if region == "jsk":
      approved=1
    endDate=datetime.date.fromordinal(datetime.date.today().toordinal()+2) 
    query="insert into broadcasts (fileid2,tfileid,approved,priority,name,vendor,type,region,template,startDate,endDate,minhour,maxhour,fileid,groups) values ('','',%s,1,'%s','any','group','%s','general',NOW(),'%s',8,20,%s,%s)" % (str(approved),bname,region,str(endDate),str(fileid),str(groupID))
  with open('/tmp/yuyy.txt', 'w') as outfile:
    outfile.write(str(form)+s)
  cur.execute(query)
 
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
 
if __name__ == '__main__':
  main()
