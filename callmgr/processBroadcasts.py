import MySQLdb
import datetime
import os


from settings import dbhost,dbuser,dbpasswd,sid,token

def singleRowQuery(cur,query):
  cur.execute(query)
  result=cur.fetchone()
  return result[0]

def main():
  todaydate=datetime.date.today().strftime("%d%B%Y")
  db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, charset='utf8')
  cur=db.cursor()
  db.autocommit(True)
  query="SET NAMES utf8"
  cur.execute(query)
  query="use libtech"
  cur.execute(query)
  query="select bid,type,minhour,maxhour,tfileid,fileid,groups,blocks,panchayats from broadcasts where approved=1 and processed=0 and startDate <= CURDATE();"
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    bid=str(row[0])
    minhour=str(row[2])
    maxhour=str(row[3])
    error=0
    print "Broadcast ID"+str(bid)
    broadcastType=row[1]
    if (broadcastType == "group"):
      #Lets get audio File names for tringo
      tringofilelist=row[4].rstrip(',')
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
      print "Tringo audio is "+tringoaudio;
      #Lets first get the audioFileNames
      filelist=row[5].rstrip(',')
      filelistArray=filelist.split(',')
      audio=''
      for audioFileID in filelistArray:
        query="select count(*) from audioLibrary where id="+audioFileID
        audioExists=singleRowQuery(cur,query)
        if (audioExists == 1):
          query="select filename from audioLibrary where id="+audioFileID
          print query
          audio+=singleRowQuery(cur,query)
        else:
          error=1
        audio+=','
      audio=audio.rstrip(',')
      print "audiolist"+audio
         
      groups=row[6].rstrip(',')
      groupArray=groups.split(',')
      groupMatchString=''
      for group in groupArray:
        query="select name from groups where id="+group
        groupName=singleRowQuery(cur,query)
        print group+groupName
        groupMatchString+="  groups like '%~"+groupName+"~%' or"
        print '\n'
      groupMatchString=groupMatchString[:-2]
      if (error == 0):
        query="select phone from addressbook where ("+groupMatchString+") and dnd='no'"
        cur.execute(query)
        results1 = cur.fetchall()
        for r in results1:
          phone=r[0]
          print phone
          query="insert into callQueue (vendor,bid,minhour,maxhour,phone,audio) values ('exotel',"+bid+","+minhour+","+maxhour+",'"+phone+"','"+audio+"');"
          cur.execute(query)
        query="select phone from addressbook where ("+groupMatchString+") and dnd !='no'"
        cur.execute(query)
        results1 = cur.fetchall()
        for r in results1:
          phone=r[0]
          print phone
          query="insert into callQueue (vendor,bid,minhour,maxhour,phone,audio) values ('tringo',"+bid+","+minhour+","+maxhour+",'"+phone+"','"+tringoaudio+"');"
          cur.execute(query)
              
        
        query="update broadcasts set processed=1 where bid="+bid
        cur.execute(query)
      else:
        query="update broadcasts set error=1 where bid="+bid
        cur.execute(query)
if __name__ == '__main__':
  main()
