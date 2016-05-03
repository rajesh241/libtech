#! /usr/bin/env python

import cgi
import cgitb; cgitb.enable() # Optional; for debugging only
import sys
import os
import MySQLdb
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
from wrappers.db import dbInitialize,dbFinalize

def main():
  print 'Content-type: text/plain'
  print 
  db = dbInitialize(db="libtech", charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  query="use libtech"
  cur.execute(query)

  form = cgi.FieldStorage()
  outfile=open('/tmp/y.txt', 'w')
  outfile.write(str(form))
  
  query="select b.bid,b.fileid,a.filename from broadcasts b,audioLibrary a where b.fileid=a.id and b.groups='1001,' order by b.bid desc limit 1;"
  cur.execute(query)
  row=cur.fetchone()
  filename=row[2]
  bid=row[0]
  phone = form['From'].value
  phone=phone[-10:]
  exophone = form['To'].value
  sid= form['CallSid'].value
  query="insert into callSummary (bid,phone,direction) values (%s,'%s','in')" % (str(bid),phone)
  outfile.write(query)
  cur.execute(query)
  callid=cur.lastrowid
  query="insert into callQueue (audio,bid,vendor,phone,sid,retry,inprogress,callRequestTime,exophone,curVendor,callid) values ('%s',%s,'exotel','%s','%s',0,1,NOW(),'%s','exotel','%s') " % (filename,str(bid),phone,sid,exophone,str(callid))
  outfile.write(query)
  cur.execute(query)
  myfile='http://libtech.info/audio/%s' %(filename)
  sys.stdout.write(myfile)


  dbFinalize(db) # Make sure you put this if there are other exit paths or errors

if __name__ == '__main__':
  main()
