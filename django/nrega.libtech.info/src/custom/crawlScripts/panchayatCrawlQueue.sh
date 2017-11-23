#!/bin/bash
#First we will kill the process if it is older than 3 hours
cd /home/libtech/repo/django/nrega.libtech.info
source bin/activate
cmd="python src/custom/crawlScripts/managePanchayatCrawlQueue.py -e -step $1 -limit $2"
#echo $cmd
#$cmd

pgrep -f "$cmd" || $cmd &> /tmp/pcq$1.log
