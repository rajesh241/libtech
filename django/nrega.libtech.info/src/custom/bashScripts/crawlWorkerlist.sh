#!/bin/bash
cd /home/libtech/repo/django/nrega.libtech.info
source bin/activate
cmd="python src/custom/scripts/crawlApplicationRegister.py -limit 50"
#echo $cmd
#$cmd
pgrep -f "$cmd" || $cmd &> /tmp/cwl.log
