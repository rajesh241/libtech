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

def gettringoaudio(rawlist):
  tringofilelist=rawlist.rstrip(',')
  tringoArray=tringofilelist.split(',')
  noOfFiles=len(tringoArray)
  i=0
  tringoaudio=''
  while(i<20):
    curFileID='27503'
    if(i < noOfFiles):
      curFileID=tringoArray[i]
    i=i+1
    tringoaudio+="&fileid"+str(i)+"="+curFileID
  return tringoaudio
def getGroupQueryMatchString(cur,rawgroup):
  groups=rawgroup.rstrip(',')
  groupArray=groups.split(',')
  queryMatchString='( '
  for group in groupArray:
    query="select name from groups where id="+group
    #print query
    groupName=singleRowQuery(cur,query)
    #print group+groupName
    queryMatchString+="  groups like '%~"+groupName+"~%' or"
    #print '\n'
  queryMatchString=queryMatchString[:-2]
  queryMatchString+=")"
  return queryMatchString
def getLocationQueryMatchString(rawdistrict,rawblock,rawpanchayat):
  district=rawdistrict
  blocks=rawblock
  panchayats=rawpanchayat
  panchayatArray=panchayats.split(',')
  #First we need to check if panchayat name contains all then we dont need to loop through all panchayats
  if 'all' in panchayatArray:
    queryMatchString="district='"+district+"' and block='"+blocks+"' "
  else:
    queryMatchString="district='"+district+"' and block='"+blocks+"' and ("
    for panchayat in panchayatArray:
      if (panchayat != '0'):
        queryMatchString+=" panchayat ='"+panchayat+"' or" 
    queryMatchString=queryMatchString[:-2]
    queryMatchString+=")"
  #print "We are in Location" 
  #print queryMatchString
  return queryMatchString

def getaudio(cur,rawlist):
  error=0
  filelist=rawlist.rstrip(',')
  filelistArray=filelist.split(',')
  audio=''
  for audioFileID in filelistArray:
    query="select count(*) from audioLibrary where id="+audioFileID
    audioExists=singleRowQuery(cur,query)
    if (audioExists == 1):
      query="select filename from audioLibrary where id="+audioFileID
#      print query
      audio+=singleRowQuery(cur,query)
    else:
      error=1
    audio+=','
  audio=audio.rstrip(',')
  return audio,error

def main():
  todaydate=datetime.date.today().strftime("%d%B%Y")
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use libtech"
  cur.execute(query)
  query="select bid,type,minhour,maxhour,tfileid,fileid,groups,vendor,district,blocks,panchayats from broadcasts where approved=1 and processed=0 and startDate <= CURDATE();"
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    bid=str(row[0])
    minhour=str(row[2])
    maxhour=str(row[3])
    tringoaudio=gettringoaudio(row[4])
    audio,error=getaudio(cur,row[5])
    vendor=row[7]
    print "Broadcast ID"+str(bid)
    print "Tringo audio is "+tringoaudio;
    print "audiolist"+audio
    print "Broadcast Type "+broadcastType
    print "QueryMatchString "+queryMatchString
    broadcastType=row[1]
    if (broadcastType == "group"):
      #Lets first get the audioFileNames
      queryMatchString=getGroupQueryMatchString(cur,row[6]) 
    elif (broadcastType == "location"):
      queryMatchString=getLocationQueryMatchString(row[8],row[9],row[10])
    else:
      error=1


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
          if( (vendor == "any") or (vendor =="tringo")):
            vendor='tringo'
        else:
          skip=1 
        print phone
        if len(phone) == 10 and phone.isdigit() and skip == 0:
          query="insert into callQueue (vendor,bid,minhour,maxhour,phone,audio,tringoaudio,exophone) values ('"+vendor+"',"+bid+","+minhour+","+maxhour+",'"+phone+"','"+audio+"','"+tringoaudio+"','"+exophone+"');"
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
