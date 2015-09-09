import MySQLdb
import datetime
import os
import sys

fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../includes/')
import libtechFunctions
import globalSettings
import settings
from settings import dbhost,dbuser,dbpasswd,sid,token
from libtechFunctions import gethtmlheader 
from libtechFunctions import gethtmlfooter 
from libtechFunctions import singleRowQuery,arrayToHTMLLine,writecsv 
from broadcastFunctions import getLocationQueryMatchString,getGroupQueryMatchString,gettringoaudio,getaudio
def main():
  todaydate=datetime.date.today().strftime("%d%B%Y")
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use libtech"
  cur.execute(query)
  query="select bid,type,minhour,maxhour,tfileid,fileid,groups,vendor,district,blocks,panchayats,priority,fileid2,template from broadcasts where error=0 and approved=1 and processed=0 and startDate <= CURDATE();"
  print query
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    bid=str(row[0])
    minhour=str(row[2])
    maxhour=str(row[3])
    tringoaudio=gettringoaudio(row[4])
    audio,error=getaudio(cur,row[5])
    #audio1,error1=getaudio(cur,row[12])
    requestedVendor=row[7]
    priority=row[11]
    template=row[13]
    print "Vendor "+requestedVendor
    broadcastType=row[1]
    if (broadcastType == "group"):
      #Lets first get the audioFileNames
      queryMatchString=getGroupQueryMatchString(cur,row[6]) 
    elif (broadcastType == "location"):
      queryMatchString=getLocationQueryMatchString(row[8],row[9],row[10])
    elif (broadcastType == "transactional"):
      queryMatchString='phone is NULL'  #We dont want any calls to be Added to Call Queue
    else:
      error=1


    print "Broadcast ID"+str(bid)
    print "Tringo audio is "+tringoaudio;
    print "audiolist"+audio
    print "Broadcast Type "+broadcastType
    print "QueryMatchString "+queryMatchString
    print "Vendor "+requestedVendor
    if (error == 0):
      query="select phone,exophone,dnd from addressbook where "+queryMatchString+" "
      print query
      cur.execute(query)
      results1 = cur.fetchall()
      for r in results1:
        phone=r[0]
        exophone=r[1]
        if exophone is None:
          exophone="08033545179"
        dnd=r[2]
        skip=0
        if(dnd == 'yes'):
          if( (requestedVendor == "any") or (requestedVendor =="tringo")):
            vendor='tringo'
          else:
            vendor="any"
            skip=1 
        else:
          vendor=requestedVendor;
        print "phone "+phone+" skip"+str(skip)+"vendor "+vendor
        if len(phone) == 10 and phone.isdigit() and skip == 0:
          query="insert into callQueue (priority,template,vendor,bid,minhour,maxhour,phone,audio,audio1,tringoaudio,exophone) values ("+str(priority)+",'"+template+"','"+vendor+"',"+bid+","+minhour+","+maxhour+",'"+phone+"','"+audio+"','"+audio+"','"+tringoaudio+"','"+exophone+"');"
          print query
          cur.execute(query)
          query="insert into callStatus (bid,phone) values ("+bid+",'"+phone+"');"
          print query
          cur.execute(query)
            
      
      query="update broadcasts set processed=1 where bid="+bid
      cur.execute(query)
    else:
      query="update broadcasts set error=1 where bid="+bid
      cur.execute(query)
if __name__ == '__main__':
  main()
