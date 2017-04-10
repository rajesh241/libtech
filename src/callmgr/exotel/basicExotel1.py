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
  print 'Content-type: text/plain'
  print 
  db = dbInitialize(db="libtech")
  cur = db.cursor()
  form = cgi.FieldStorage()
  if form.has_key('CustomField'):# is not None:
    callid = form['CustomField'].value
    query="select audio1 from callQueue where callid=%s" % callid
  elif form.has_key('From'):
    phone=form['From'].value
    sid=form['CallSid'].value
    last10Phone=phone[-10:]
    query="select audio1 from callQueue where isTest=1 and sid='%s'" % sid
  else:
    query="select filename from audioLibrary where id=1579"
  with open('/tmp/y.txt', 'w') as outfile:
    outfile.write(str(form)+query)
  cur.execute(query)
  if cur.rowcount == 1:
    row=cur.fetchone()
    audioFiles=row[0]
    audioFileList=audioFiles.split(',')
    for audio in audioFileList:
      print "http://callmgr.libtech.info/open/audio/%s" % audio;
  else:
    print "http://callmgr.libtech.info/open/audio/1653_ResearchRSCDR2p28000.wav"
if __name__ == '__main__':
  main()
