#!/bin/bash
cd /home/libtech/repo/django/nrega.libtech.info
source bin/activate
cmd="python src/custom/scripts/dm.py -n $1 -q $2"
#echo $cmd
#$cmd
pgrep -f "$cmd" || $cmd &> /tmp/dmcron.log
