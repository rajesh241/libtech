#!/bin/bash
cd /home/libtech/repo/django/nrega.libtech.info
source bin/activate
cmd="python src/custom/scripts/processMusters.py -s $1 -limit 5000 "
#echo $cmd
#$cmd
pgrep -f "$cmd" || $cmd &> /tmp/$1_pm.log
