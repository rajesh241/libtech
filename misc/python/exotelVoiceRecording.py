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
  digits = form['digits'].value
  upload_date = form['CurrentTime'].value
  url = form['RecordingUrl'].value
  mp3_file = url.split('/')[-1]
  wave_file = mp3_file.replace('.mp3', '.wav')

  cmd = 'cd /home/libtech/webroot/broadcasts/audio/surgujaVoiceRecordingMP3 && wget ' + url
  os.system(cmd)

  cmd = 'cd /home/libtech/webroot/broadcasts/audio/surgujaVoiceRecordingMP3 && ffmpeg -i ' + mp3_file + ' -ac 1 -ar 8000 ' + wave_file
  os.system(cmd)

  db = dbInitialize(db="libtech")
  cur = db.cursor()
  query = 'insert into exotelRecordings (sid, filename, recordCreateDate, url, phone, exotelUploadDate, exotelRecordingGood) values ("%s", "%s", now(), "%s", "%s", "%s", %s)' % (sid, wave_file, url, phone, upload_date, digits)
  cur.execute(query)
  dbFinalize(db)
    
if __name__ == '__main__':
  main()
