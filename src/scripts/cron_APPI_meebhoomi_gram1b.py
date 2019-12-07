import os
import time

cmd = 'rm -rf /tmp/tmp*; pkill Xvfb; pkill Xephyr'

if time.time() - os.path.getmtime('/home/mayank/libtech/src/scripts/nohup.out') > 180:
	os.system(cmd)

