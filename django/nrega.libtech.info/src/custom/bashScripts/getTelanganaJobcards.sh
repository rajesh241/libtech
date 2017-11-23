#!/bin/bash
cd /home/libtech/repo/django/nrega.libtech.info
source bin/activate
cmd="python src/custom/cronScripts/getTelanganaJobcards.py -d -limit $1"
pgrep -f "$cmd" || $cmd &> /tmp/ctj.log
cmd="python src/custom/cronScripts/getTelanganaJobcards.py -p -limit $1"
pgrep -f "$cmd" || $cmd &> /tmp/ctj.log
