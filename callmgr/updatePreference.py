import MySQLdb
import datetime
import os
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../includes/')
import time
from settings import dbhost,dbuser,dbpasswd,sid,token

def main():
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use libtech"
  cur.execute(query)
  query="update callQueue set preference=preference+priority where inprogress=0;" 
  cur.execute(query)

if __name__ == '__main__':
  main()
