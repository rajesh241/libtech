#!/bin/bash
cd /home/libtech/repo/django/nrega.libtech.info
source bin/activate
cmd="python src/custom/cronScripts/processApplicationRegister.py -limit $1"
#echo $cmd
#$cmd
pgrep -f "$cmd" || $cmd &> /tmp/pwl.log
