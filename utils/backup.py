##This script Backsup the databases
##It takes two parameters
# File which has all the databases that need to be backedup
# It takes the type of backup as command line input
#if type of backup is daily, it would append the day of week as suffix to file
#if the type of backup is weekly, it would append no of week of month as suffix
#if the type of backup is monthly it would append the month as suffix

#So to run to dbbackup.py daily|monthly|weekly

from backupfunctions import savedb
import sys
import MySQLdb
import datetime
import os
import time
import math
import datetime

BACKUP_PATH="~/backup/data/db/"
DB_NAMES = '/home/libtech/backup/scripts/dbnames.txt'
def main():
  suffix="none"
  backupType=sys.argv[1]
  if(backupType == "daily"):
    suffix=(time.strftime("%a"))
  elif(backupType =="weekly"):
    day_of_month = datetime.datetime.now().day
    suffix = (day_of_month - 1) // 7 + 1
  elif(backupType =="monthly"):
    suffix=(time.strftime("%b"))

  
  in_file = open(DB_NAMES,"r")
  flength = len(in_file.readlines())
  in_file.close()
  p = 1
  dbfile = open(DB_NAMES,"r")

  while p <= flength:
    db = dbfile.readline()   # reading database name from file
    db = db[:-1]         # deletes extra line
    if(suffix != "none"):
      filename=db+"_"+str(suffix)
      filepath=BACKUP_PATH+backupType
      savedb(db,filename,filepath)
    p=p+1

if __name__ == '__main__':
  main()
