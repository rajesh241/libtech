#!/bin/bash
cd /home/libtech/repo/django/nrega.libtech.info
source bin/activate
cmd="python src/custom/cronScripts/crawlMusters.py -cr $1 -limit $2"
#echo $cmd
#$cmd
pgrep -f "$cmd" || $cmd &> /tmp/cm.log
