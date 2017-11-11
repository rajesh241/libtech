#!/bin/bash
#First we will kill the process if it is older than 3 hours
myPID=`ps -ef | grep dm.py | grep -v grep | awk '{print $2}'`
echo $myPID
myTime=`ps -o etimes= -p "$myPID"`
echo $myTime
if [ $myTime -gt 10000 ]
  then 
    echo "Time is about 3 hours"
    kill -9 $myPID
fi
cd /home/libtech/repo/django/nrega.libtech.info
source bin/activate
cmd="python src/custom/cronScripts/dm.py -n $1 -q $2 -cr $3 -f 18"
#echo $cmd
#$cmd

pgrep -f "$cmd" || $cmd &> /tmp/dmcroncustom.log
