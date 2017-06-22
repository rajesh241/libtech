#!/bin/bash
cd /home/libtech/repo/django/nrega.libtech.info
source bin/activate
cmd="python src/custom/scripts/crawlMusters.py -limit 100"
#echo $cmd
#$cmd
pgrep -f "$cmd" || $cmd &> /tmp/cm.log
