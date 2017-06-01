#!/bin/bash
cd /home/libtech/repo/django/nrega.libtech.info
source bin/activate
cmd="python src/custom/scripts/crawlMusters.py -f 18 -limit 200"
#echo $cmd
#$cmd
pgrep -f "$cmd" || $cmd &> /tmp/dm.log
