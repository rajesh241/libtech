#!/bin/bash
cd /home/libtech/repo/django/nrega.libtech.info
source bin/activate
cmd="python src/custom/scripts/dm.py -b chrome -n 20 -q 40000 -s 15"
#echo $cmd
#$cmd
pgrep -f "$cmd" || $cmd &> /tmp/dm.log
