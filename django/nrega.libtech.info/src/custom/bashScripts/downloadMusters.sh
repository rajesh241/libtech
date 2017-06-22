#!/bin/bash
cd /home/libtech/repo/django/nrega.libtech.info
source bin/activate
cmd="python src/custom/scripts/dm.py -b phantomjs -n 25 -q 50000 -p  3406007011"
#echo $cmd
#$cmd
pgrep -f "$cmd" || $cmd &> /tmp/dm.log
