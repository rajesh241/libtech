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
  phone=form['From'].value
  sid=form['CallSid'].value
  last10Phone=phone[-10:]
  query="select filename from exotelRecordings where sid='%s'" % sid
  cur.execute(query)
  row=cur.fetchone()
  filename=row[0]

  myaudio="http://callmgr.libtech.info/open/audio/surgujaVoiceRecordingMP3/%s" % filename
  print myaudio
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
if __name__ == '__main__':
  main()
