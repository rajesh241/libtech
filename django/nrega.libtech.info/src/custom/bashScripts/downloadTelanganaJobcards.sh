#!/bin/bash
cd /home/libtech/repo/django/nrega.libtech.info
source bin/activate
cmd="python /home/libtech/repo/django/nrega.libtech.info/src/custom/scripts/getTelanganaJobcardDetails.py -d -n 40 -q 2000 "
#echo $cmd
#$cmd
pgrep -f "$cmd" || $cmd &> /tmp/td.log
