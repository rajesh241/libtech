#! /usr/bin/env python

import cgi
import cgitb; cgitb.enable() # Optional; for debugging only

import os
import sys
dirname = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dirname+'/../../../pds/scripts/')
rootdir = os.path.dirname(os.path.dirname(os.path.dirname(dirname)))

from pdsFunctions import cleanFPSName,writeFile
from pdsReport import getPDSAudioList
from pdsSettings import pdsDB,pdsDBHost,pdsRawDataDir,pdsWebDirRoot,pdsUIDir,pdsAudioDir
import sys
sys.path.insert(0, rootdir)


from wrappers.db import dbInitialize,dbFinalize


def main():
  print 'Content-type: text/plain'
  print 
  db = dbInitialize(db='libtech')
  cur = db.cursor()
  form = cgi.FieldStorage()
# phone=form['From'].value
# sid=form['CallSid'].value
# last10Phone=phone[-10:]
  digits=form['digits'].value
  digits=digits.strip('"')
  with open('/tmp/bihar1.txt', 'w') as outfile:
    outfile.write(str(form)+digits)
 # digits='12380030041412'
  fpsCode=digits[:-2]
  month=int(digits[-2:])

  audioFiles=getPDSAudioList(fpsCode,month)
  if audioFiles is not None:
    audioFileList=audioFiles.split(',')
    s=''
    for audioID in audioFileList:
      query="select filename from audioLibrary where id=%s " % str(audioID)
      cur.execute(query)
      row=cur.fetchone()
      audio=row[0]
      s+=audio
      print "http://callmgr.libtech.info/open/audio/%s" % audio;
    with open('/tmp/bihar.txt', 'w') as outfile:
      outfile.write(str(form)+s)
  else:
    audioFile="spss_try_again.wav"
    print "http://callmgr.libtech.info/open/audio/prompts/%s" % audioFile
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
if __name__ == '__main__':
  main()
