#!/bin/bash
#First we will kill the process if it is older than 3 hours
cd /home/libtech/work/venvs/libtech
source bin/activate
cd /home/libtech/repo/django/n.libtech.info
cmd="python src/custom/scripts/populateBlocksPanchayats.py"
echo $cmd
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
  if [ $myTime -gt 30000 ]
    then 
      echo "Time is about 3 hours"
      kill -9 $myPID
  fi
fi
pgrep -f "$cmd" || $cmd &> /tmp/populate.log
