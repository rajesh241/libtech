#! /usr/bin/env python

import cgi
import cgitb; cgitb.enable() # Optional; for debugging only

import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(os.path.dirname(os.path.dirname(dirname)))

import sys
sys.path.insert(0, rootdir)


from wrappers.db import dbInitialize,dbFinalize


def main():
  print 'Content-type: text/html'
  print 
  dirname="/home/libtech/webroot/callmgr.libtech.info/open/audio/libtechFlow/"
  outputdirname="/home/libtech/webroot/callmgr.libtech.info/open/audio/"
  db = dbInitialize(db="libtech")
  cur = db.cursor()
  form = cgi.FieldStorage()
  with open('/tmp/z.txt', 'w') as outfile:
    outfile.write(str(form))

  sid = form['CallSid'].value
  phone = form['From'].value
  last10Phone=phone[-10:]
  #upload_date = form['CurrentTime'].value
  upload_date=''
  urlString = form['RecordingUrl'].value
  urlArray=urlString.split(',')
  url=urlArray[-1]
  mp3_file = url.split('/')[-1]
  wave_file = mp3_file.replace('.mp3', '.wav')
  filename = mp3_file.replace('.mp3', '')
  query="insert into audioLibrary (name) values ('%s')" % filename
  cur.execute(query)
  audioID=str(cur.lastrowid)
  with open('/tmp/z.txt', 'a') as outfile:
    outfile.write("Before CMD audioID[%s],sid[%s], phone[%s],  upload_date[%s], url[%s], mp3_file[%s], wave_file[%s]" % (audioID,sid, phone,  upload_date, url, mp3_file, wave_file))

  import os
  cmd = 'cd %s && wget %s' % (dirname,url)
  os.system(cmd)
  with open('/tmp/z.txt', 'a') as outfile:
    outfile.write(str(cmd))
  wave_fileName="%s_%s.wav" % (audioID,filename)
  query="update audioLibrary set filename='%s' where id=%s " % (wave_fileName,audioID)
  cur.execute(query)
  cmd = 'cd ' + dirname + ' && ffmpeg -i ' + mp3_file + ' -ac 1 -ar 8000 ' + outputdirname+wave_fileName
  os.system(cmd)
  with open('/tmp/z.txt', 'a') as outfile:
    outfile.write(str(cmd))

  query = 'insert into exotelRecordings (sid, filename, recordCreateDate, url, phone, exotelUploadDate, exotelRecordingGood) values ("%s", "%s", now(), "%s", "%s", NOW(),1)' % (sid, wave_fileName, url, last10Phone)
  with open('/tmp/z.txt', 'a') as outfile:
    outfile.write(query)
  cur.execute(query)
  dbFinalize(db)

  '''
  cmd = 'cd /home/libtech/webroot/broadcasts/audio/surgujaVoiceRecordingMP3 && cp ../' + wave_file + ' current.wav'
  os.system(cmd)
  with open('/tmp/z.txt', 'a') as outfile:
    outfile.write(cmd)
  '''

  return 0
    
if __name__ == '__main__':
  main()
