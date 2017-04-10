#!/usr/bin/env python3

import os
import sys
if sys.stdout.encoding != 'UTF-8':   # Figure a way to modify it from within - Mynk
  os.putenv("PYTHONIOENCODING",'UTF-8')
  os.execv(sys.executable,['python3']+sys.argv)

fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../../wrappers/')
sys.path.insert(0, fileDir+'/../../../utils/')

import cgi
import cgitb; cgitb.enable() # Optional; for debugging only
from db import dbInitialize,dbFinalize


from bootstrap import bsQuery2Html, htmlWrapper, getForm, getCenterAligned
from queryDashboard import getQueryTable, queryDB

def main():
  print('Content-type: text/html')

  db = dbInitialize(db="libtech", charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use libtech"
  cur.execute(query)
  
  form = cgi.FieldStorage()
  formType=form["formType"].value
  qid=form["qid"].value
  myhtml=""

  query = ""
  if form.__contains__("query"):
    query = form["query"].value
    
  if query[0:7] != "select ":
    myhtml+= '<br />' + getCenterAligned('<h5 style="color:red"> ERROR: Tried [%s]. Only "select ...." queries allowed</h5>' % (query))
  elif(formType == 'queryMake'):
    myhtml+=bsQuery2Html(cur,query)
    #myhtml += getForm(0, './queryDashboardPost.py', 'queryMake', 'Go', query)
    myhtml += getForm(0, './queryDashboardPost.py', 'queryAdd', 'Add', query)
  elif(formType == 'queryAdd'):
    cur.execute('insert into queryDB (query) VALUES ("%s")' % query)
    myhtml+=getQueryTable(cur)
    myhtml+= '<br />' + getCenterAligned('<h5 style="color:green">Query [%s] Added</h5>' % query)
  elif(formType == 'queryDelete'):
    query='delete from queryDB where qid=' +  str(qid)
    cur.execute(query)
    myhtml+='<h3>Vendor has been updated for %s</h3>' %(str(bid))
  else:
    myhtml+= getCenterAligned('<h5> Error Tried %s</h5>' % (formType)) 

  myhtml+= '<br />' + getCenterAligned('<h5>Return to the <a href="./queryDashboard.py">Query Dashboard</a></h5>')

  myhtml=htmlWrapper(title="Query Dashboard", head='<h1 aling="center"><a href="./queryDashboard.py">Query Dashboard</a></h1>', body=myhtml)
  dbFinalize(db)
  print(myhtml)

if __name__ == '__main__':
  main()
