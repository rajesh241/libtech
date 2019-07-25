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
  db = dbInitialize(db="libtech")
  cur = db.cursor()
  form = cgi.FieldStorage()
  with open('/tmp/m.txt', 'w') as outfile:
    outfile.write(str(form))
 
  phone1 = form['From'].value
  phone=phone1[-10:]
  exophone = form['To'].value
  query="insert into missedCalls (phone,exophone) values ('%s','%s');" % (phone,exophone)
  cur.execute(query) 
  isAdmin=1
  if isAdmin == 1:
    print 'Status: 200 OK'
    print 
  else:
    print 'Status: 302 Found'
    print 
  
if __name__ == '__main__':
  main()
