#!/usr/bin/env python

import cgi
import cgitb; cgitb.enable() # Optional; for debugging only
import MySQLdb
import math
import datetime
import os
import time
import requests
import xml.etree.ElementTree as ET
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../../includes/')
sys.path.insert(0, fileDir+'/../../')
import libtechFunctions
import globalSettings
import settings
import processBroadcasts
from processBroadcasts import getGroupQueryMatchString,getLocationQueryMatchString 
from settings import dbhost,dbuser,dbpasswd,sid,token
from libtechFunctions import gethtmlheader 
from libtechFunctions import gethtmlfooter 
from libtechFunctions import singleRowQuery,arrayToHTMLLine,writecsv 
from globalSettings import broadcastsReportFile,broadcastReportFilePath


def htmlWrapper(title = None, head = None, body = None):
  html_text = '''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    
    <title>title_text</title>

    <!-- Bootstrap -->

    <!-- Latest compiled and minified CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css">

    <!-- Optional theme -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap-theme.min.css">

    <div align="center">head_text</div>

  </head>
    
  <body>

    body_text
    
    <!-- jQuery (necessary for Bootstrap"s JavaScript plugins) -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->

    <!-- Latest compiled and minified JavaScript -->
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>

  </body>
</html>
'''
  html_text = html_text.replace('title_text', title)
  html_text = html_text.replace('head_text', head)
  html_text = html_text.replace('body_text', body)

  return html_text


def getTableHtml(cur, query, query_caption=None, field_names=None, extra=None):

  cur.execute(query)
  results = cur.fetchall()

  if query_caption == None:
    query_caption = "Query:"

  if field_names == None:
    field_names = [i[0] for i in cur.description]
  num_fields = len(cur.description)
  
  table_html='''
<div class="container">
  <h2>query_caption</h2>
  <pre>    query_text</pre>
  <table class="table table-striped">
    <thead>
      <tr>
      '''

  for field_name in field_names:
    table_html += "<th>" + field_name.strip() + "</th>"

  table_html += '''
      </tr>
    </thead>
    <tbody>
      <tr>
      '''
  
  for row in results:
    table_html += "<tr>"

    i = 0
    while i < num_fields:
      table_html += "<td>" + str(row[i]) + "</td>"
      i += 1

    if extra != None:
      table_html += "<td>" + extra.replace('section_tag',str(row[0])).replace('section_text',str(row[0])) + "</td>"

    table_html += "</tr>"

  table_html += '''
      <tr>
        <td colspan="colspan_value"><div align=center><a href="#"><h5>Top</h5></a></div></td>
      </tr>
    </tbody>
  </table>
</div>
  '''
  return table_html.replace('query_caption', query_caption).replace('query_text', query).replace('colspan_value', str(num_fields))

def TBD():
  form_html = '''
  <form>
    <div class="row">
      <div class="col-xs-6">
        <div class="input-group">
          <input type="text" class="form-control" placeholder="Query...">
          <span class="input-group-btn">
            <button type="button" class="btn btn-default">Go</button>
            <button type="button" class="btn btn-default">Add</button>            
          </span>
        </div>
      </div>
      <div class="col-xs-6">
        <div class="input-group">
          <span class="input-group-btn">
            <button type="button" class="btn btn-default">Action</button>
            <button type="button" class="btn btn-default">Options</button>
          </span>
          <input type="text" class="form-control"  placeholder="Add query...">
        </div>
      </div>
    </div>
  </form>
'''



def getForm(qid, form_type, button_text, query_text = None):
  if query_text == None:
    query_text = ''
    
  form_html = '''
  <form action="./queryDashboardPost.py" method="POST">
    form_text
  </form>
'''
  form_text = '''
    <div class="row">

      <div class="col-xs-2">
      </div>

      <div class="col-xs-8">
        <div class="input-group">
          <input name="qid" value="qid_value" type="hidden">
          <input name="formType" value="form_type" type="hidden">
          <input name="query" type="text" class="form-control" placeholder="Query..." value="query_text">
          <span class="input-group-btn">
            <button type="submit" class="btn btn-default">button_text</button>
          </span>
        </div>
      </div>

      <div class="col-xs-2">
      </div>

    </div>
'''
  form_text = form_text.replace('qid_value', str(qid))
  form_text = form_text.replace('form_type', form_type)
  form_text = form_text.replace('button_text', button_text)
  form_text = form_text.replace('query_text', query_text)

  input_element = '''
        <div class="input-group">
          <input type="text" class="form-control" placeholder="Query...">
        </div>
'''  

  formhtml='<br /><form action="./queryDashboardPost.py" method="POST"><input name="qid" value="%s" type="hidden"><input name="formType" value="%s" type="hidden"></input>%s<button type="submit">%s</button></form>' %(qid, form_type, input_element, "Go")
  
#  return formhtml
  return form_html.replace('form_text', form_text)

def getQueryTable(cur):
  query = 'select * from queryDB'
  field_names = ['Query No', 'Query', 'Go To']
  section_html = '<a href="#querysection_tag">section_text</a>'
  
  query_table = "<br />"
  query_table += getTableHtml(cur, query, query_caption="", field_names=field_names, extra=section_html)
  query_table += getForm(0, 'queryMake', 'Go')
  return query_table
  

def queryDB():
  print 'Content-type: text/html'
  print 
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
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
    myhtml += getTableHtml(cur,query, query_caption)
    myhtml += "<br />"
  
  myhtml=htmlWrapper(title="Query Dashboard", head='<h1 aling="center"><a href="./queryDashboard.py">Query Dashboard</a></h1>', body=myhtml)
  return myhtml


def main():
  print queryDB()

if __name__ == '__main__':
  main()
