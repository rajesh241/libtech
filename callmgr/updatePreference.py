import MySQLdb
import datetime
import os
import sys
import math
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
  query="select c.callid,c.phone,c.priority,c.preference,a.successPercentage from callQueue c, addressbook a where c.phone=a.phone"
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    callid=str(row[0])
    phone=row[1]
    priority=row[2]
    preference=row[3]
    successPercentage=row[4]
    newPreference=preference+(priority*successPercentage)
    print " Phone : %s, successPercentage %s, priority %s, preference %s, newPreference %s " % (phone,str(successPercentage),str(priority),str(preference),str(newPreference))
    query="update callQueue set preference=%s where callid=%s" % (str(newPreference),callid)
    print query
  #query="update callQueue set preference=preference+priority where inprogress=0;" 
    cur.execute(query)

if __name__ == '__main__':
  main()
