#!/bin/bash
#First we will kill the process if it is older than 3 hours
cd /home/libtech/work/venvs/libtech
source bin/activate
cd /home/libtech/repo/django/n.libtech.info
cmd="python src/custom/crawlScripts/initiateCrawl.py -i -l debug"
echo $cmd
$cmd &
