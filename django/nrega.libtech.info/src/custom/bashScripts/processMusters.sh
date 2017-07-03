#!/bin/bash
cd /home/libtech/repo/django/nrega.libtech.info
source bin/activate
cmd="python src/custom/scripts/processMusters.py -limit 5000 "
#echo $cmd
#$cmd
pgrep -f "$cmd" || $cmd &> /tmp/pm.log
