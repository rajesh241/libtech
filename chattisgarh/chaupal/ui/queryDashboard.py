#!/usr/bin/env python

import os
import sys

fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../../includes/')
sys.path.insert(0, fileDir+'/../../../wrappers/')
sys.path.insert(0, fileDir+'/../../../utils/')

import cgitb; cgitb.enable() # Optional; for debugging only
from db import dbInitialize,dbFinalize


from bootstrap_utils import bsQuery2Html, htmlWrapper, getForm, getCenterAligned

def getQueryTable(cur):
  query = 'select * from queryDB'
  field_names = ['Query No', 'Query', 'Go To']
  section_html = '<a href="#querysection_tag">section_text</a>'
  
  query_table = "<br />"
  query_table += bsQuery2Html(cur, query, query_caption="", field_names=field_names, extra=section_html)
  query_table += getForm(0, './queryDashboardPost.py', 'queryMake', 'Go')
  return query_table

def queryDB():
  print('Content-type: text/html')

  db = dbInitialize(db="libtech", charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use libtech"
  cur.execute(query)
  query='select qid,query from queryDB'
  cur.execute(query)
  queries = cur.fetchall()

  myhtml = getQueryTable(cur)
  
  for row in queries:
    qid = row[0]
    query = row[1]
    query_caption = '<div id=query%d>Query: #%d <a name=query%d></a></div>' % (qid, qid, qid)
#    query_caption = 'Query <a href="#%d">#%d</a>' % (qid, qid)
    myhtml += bsQuery2Html(cur,query, query_caption)
    myhtml += getCenterAligned('<a href="#"><h5>Top</h5></a></div>') + '<br />'
  
  myhtml=htmlWrapper(title="Query Dashboard", head='<h1 aling="center"><a href="./queryDashboard.py">Query Dashboard</a></h1>', body=myhtml)

  dbFinalize(db)
  return myhtml  # .encode('UTF-8') # .encode('ascii','xmlcharrefreplace') 


def main():
  print(queryDB())

  #res = queryDB()   #
  #print(str(res, encoding="UTF-8"))

  '''
  if type(res) is bytes:
   print(str(res, encoding="UTF-8"))
   #print(res)
   # sys.stdout.buffer.write(res)
  else:
    print(type(res))
    print(sys.stdout.encoding)
    #sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

    tmpout = sys.stdout
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print(sys.stdout.encoding)
    sys.stdout = tmpout
  '''

if __name__ == '__main__':
  main()
