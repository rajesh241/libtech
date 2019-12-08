#!/usr/bin/env python3

import os
import time
import psutil

#print('Running the CRON')

script_name = 'APPI_meebhoomi_gram1b.py' # 'python3 APPI_meebhoomi_gram1b.py'
cmd = 'rm -rf /tmp/tmp*; pkill Xvfb; pkill Xephyr'

#if time.time() - os.path.getmtime('/home/mayank/libtech/src/scripts/nohup.out') > 180:
if time.time() - os.path.getmtime('/tmp/appi.log') > 180:
        for proc in psutil.process_iter():
                # check whether the process name matches
                if script_name in proc.name():
                        proc.kill()
        os.system(cmd)
        os.system('cd /home/mayank/libtech/src/scripts && nohup python3 APPI_meebhoomi_gram1b.py TestSuite.test_fetch_appi_report &')


