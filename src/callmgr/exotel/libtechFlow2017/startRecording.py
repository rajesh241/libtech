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
  print 'Content-type: text/plain'
  print 
  db = dbInitialize(db="libtech")
  cur = db.cursor()
  form = cgi.FieldStorage()
  with open('/tmp/y.txt', 'w') as outfile:
    outfile.write(str(form))
  exophone=form['To'].value
  query="select region from regions where exophone='%s' " % exophone
  cur.execute(query)
  row=cur.fetchone()
  region=row[0]
  if region == 'spss':
    audioFile="spss_initiate_recording.wav"
#  elif region == 'jsk':
#    audioFile='initiate_recording.wav'
  else:
    audioFile="spss_initiate_recording.wav"
  print "http://callmgr.libtech.info/open/audio/prompts/%s" % audioFile
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
 
if __name__ == '__main__':
  main()
