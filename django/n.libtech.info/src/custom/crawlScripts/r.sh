#!/bin/bash
#First we will kill the process if it is older than 3 hours
echo "Wow cool"
cd /home/libtech/work/venvs/libtech
source bin/activate
cd /home/libtech/repo/django/n.libtech.info
cmd="python src/custom/crawlScripts/a.py "
#cmd="python src/custom/crawlScripts/crawlMain.py -e -l debug -step $1 "
#pgrep -f "$cmd" || $cmd &> /tmp/cq$1.log
