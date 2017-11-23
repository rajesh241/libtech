#!/bin/bash
cd /home/libtech/repo/django/nrega.libtech.info
source bin/activate
cmd="python src/custom/cronScripts/pm.py -q $2 -n $1 "
#echo $cmd
#$cmd
pgrep -f "$cmd" || $cmd &> /tmp/pmcron.log
