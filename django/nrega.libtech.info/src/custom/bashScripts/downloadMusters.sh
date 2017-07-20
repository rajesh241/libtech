#!/bin/bash
cd /home/libtech/repo/django/nrega.libtech.info
source bin/activate
cmd="python src/custom/scripts/dm.py -b chrome -n $2 -q $3 -s $1"
#echo $cmd
#$cmd
pgrep -f "$cmd" || $cmd &> /tmp/$1.log
