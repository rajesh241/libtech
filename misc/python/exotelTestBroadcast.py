#! /usr/bin/env python

import cgi
import cgitb; cgitb.enable() # Optional; for debugging only

import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(os.path.dirname(dirname))

import sys
sys.path.insert(0, rootdir)


from wrappers.db import dbInitialize,dbFinalize


def main():
  print 'Content-type: text/html'
  print 

  form = cgi.FieldStorage()
  with open('/tmp/z.txt', 'w') as outfile:
    outfile.write(str(form))

  sid = form['CallSid'].value
  phone = form['From'].value
  digits = form['digits'].value.replace('"','')

  import os

  db = dbInitialize(db="libtech")
  cur = db.cursor()
  query="select a.filename,b.bid from broadcasts b, audioLibrary a where b.bid=%s and b.fileid=a.id" % (digits);
  cur.execute(query)
  row=cur.fetchone()
  filename=row[0]
  
  query = 'insert into testBroadcast (sid,vendor,phone,callStartTime,bid,filename) values ("%s", "exotel","%s", now(), "%s","%s")' % (sid, phone,digits,filename)
  with open('/tmp/z.txt', 'a') as outfile:
    outfile.write(query)
  cur.execute(query)
  dbFinalize(db)

  return 0
    
if __name__ == '__main__':
  main()
