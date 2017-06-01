#!/bin/bash
cd /home/libtech/repo/django/nrega.libtech.info
source bin/activate
cd src/custom/biharPDS/
python crawlFPSShops.py -e
python downloadFPSData.py 
python processFPSData.py
