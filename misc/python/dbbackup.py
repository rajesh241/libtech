##This script Backsup the databases
##It takes two parameters
# File which has all the databases that need to be backedup
# It takes the type of backup as command line input
#if type of backup is daily, it would append the day of week as suffix to file
#if the type of backup is weekly, it would append no of week of month as suffix
#if the type of backup is monthly it would append the month as suffix

#So to run to dbbackup.py daily|monthly|weekly

import sys
import MySQLdb
import datetime
import os
import time
import math
import datetime
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'./')
from settings import dbhost,dbuser,dbpasswd,sid,token
from globalSettings import dbBackupDir
from dbNames import dbNames
#BACKUP_PATH="~/backup/data/db/"

def savedb(db,filename,filepath):
  fullfilepath=filepath+filename
  dumpcmd = "mysqldump -h "+dbhost+"  -u " + dbuser + " -p" + dbpasswd + " " + db + " | gzip -c | cat > " + filepath + "/" + filename + ".sql.gz" 
  os.system(dumpcmd)

def main():
  suffix="none"
  backupType=sys.argv[1]
  filepath=dbBackupDir+backupType
  if(backupType == "daily"):
    suffix=(time.strftime("%a"))
  elif(backupType =="weekly"):
    day_of_month = datetime.datetime.now().day
    suffix = (day_of_month - 1) // 7 + 1
  elif(backupType =="monthly"):
    suffix=(time.strftime("%b"))
  elif(backupType =="latest"):
    suffix='latest'
  elif(backupType == "random"):
    suffix=todaydate=datetime.date.today().strftime("%d%B%Y")
  
  dbList=dbNames.split(",")
  for db in dbList:
    print db
    if(suffix != "none"):
      filename=db+"_"+str(suffix)
      savedb(db,filename,filepath)

if __name__ == '__main__':
  main()
