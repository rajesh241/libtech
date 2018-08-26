#!/bin/bash
#First we will kill the process if it is older than 3 hours
while true
do 
  python crawlMain.py -e -l debug  -step $1 -downloadLimit  $2
done
