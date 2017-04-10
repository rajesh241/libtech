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
  with open('/tmp/y.txt', 'w') as outfile:
    outfile.write(str(form))
    
  sid = form['CallSid'].value
  phone = form['From'].value
  digits = form['digits'].value
  upload_date = form['CurrentTime'].value
  url = form['RecordingUrl'].value
  mp3_file = url.split('/')[-1]
  wave_file = mp3_file.replace('.mp3', '.wav')
  with open('/tmp/y.txt', 'a') as outfile:
    outfile.write("Before CMD sid[%s], phone[%s], digits[%s], upload_date[%s], url[%s], mp3_file[%s], wave_file[%s]" % (sid, phone, digits, upload_date, url, mp3_file, wave_file))

  name = phone + '_' + wave_file.strip('.wav')
  
  db = dbInitialize(db="libtech")
  cur = db.cursor()
  query="update exotelRecordings set inputCode='%s' where sid='%s'" % (str(digits),str(sid))
  with open('/tmp/y.txt', 'a') as outfile:
    outfile.write(query)
  cur.execute(query)
  query = 'insert into audioLibrary (name) values ("%s")' % (name)
  with open('/tmp/y.txt', 'a') as outfile:
    outfile.write(query)
#  cur.execute(query)
  query = 'select id from audioLibrary where name="%s"' % (name)
  with open('/tmp/y.txt', 'a') as outfile:
    outfile.write(query)
#  cur.execute(query)
  id = '12345' # Mynk
  filename = id + '_' + phone
  query = 'update audioLibrary filename="%s" where name="%s"' % (filename, name)
  with open('/tmp/y.txt', 'a') as outfile:
    outfile.write(query)
#  cur.execute(query)

  query = 'insert into broadcasts (name, ts, fileid) values ("%s", now(), "%s")' % (name, id)
  with open('/tmp/y.txt', 'a') as outfile:
    outfile.write(query)
#  cur.execute(query)

  dbFinalize(db)

                  

  return 0
    
if __name__ == '__main__':
  main()
