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
  phone1=form['From'].value
  phone=phone1[-10:]
 #query="select audio from callQueue where phone='%s' order by callid DESC limit 1 " % phone
 #cur.execute(query)
 #if cur.rowcount == 0:
  query="select audio from callSummary where phone='%s' order by callid DESC limit 1" % phone
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
    print "http://callmgr.libtech.info/open/audio/prompts/noNewMessage.wav"
if __name__ == '__main__':
  main()
