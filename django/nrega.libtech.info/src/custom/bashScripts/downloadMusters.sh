#!/bin/bash
cd /home/libtech/repo/django/nrega.libtech.info
source bin/activate
cmd="python src/custom/scripts/dm.py -b phantomjs -n 25 -q 500"
#echo $cmd
#$cmd
pgrep -f "$cmd" || $cmd &> /tmp/dm.log
