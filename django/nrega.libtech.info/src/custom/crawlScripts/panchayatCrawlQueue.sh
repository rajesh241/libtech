#!/bin/bash
#First we will kill the process if it is older than 3 hours
cd /home/libtech/repo/django/nrega.libtech.info
source bin/activate
cmd="python src/custom/crawlScripts/managePanchayatCrawlQueue.py -e -step $1 -limit $2"
#echo $cmd
#$cmd
myPID=$(pgrep -f "$cmd")
echo $myPID
if [ -z "$myPID" ]
then
  echo "Variable is empty"
else
  echo "Variable is not empty"
  myTime=`ps -o etimes= -p "$myPID"`
  echo $myTime
  if [ $myTime -gt 900 ]
    then 
      echo "Time is about 3 hours"
      kill -9 $myPID
  fi
fi
pgrep -f "$cmd" || $cmd &> /tmp/pcq$1.log
