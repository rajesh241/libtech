#!/usr/bin/env python3

import os
import time
import psutil

#print('Running the CRON')

script_name = 'APPI_meebhoomi_gram1b.py' # 'python3 APPI_meebhoomi_gram1b.py'
cmd = 'rm -rf /tmp/tmp*; rm -rf /tmp/rust_mozprofilef*; pkill Xvfb; pkill Xephyr'

#filename = '/home/mayank/libtech/src/scripts/nohup.out'
filename = '/tmp/appi.log'

if time.time() - os.path.getmtime(filename) > 180:
        try:
                with open(filename, 'r') as log_file:
                        print('Reading [%s]' % filename)
                        log_content = log_file.read()                        
        except Exception as e:
                print('Exception when opening file for captcha_id[%s] - EXCEPT[%s:%s]' % (captcha_text, type(e), e))
                #raise e

        tail = log_content[-95:] 
        # print(tail)
        '''
        switch_index = tail.find('Switching Window')
        print('Switch index [%s]' % switch_index)
        '''
        if 'Switching Window' not in tail:
                exit(0)
        verify_str = 'Verifying File ['
        begin = log_content.rfind(verify_str) + len(verify_str)
        end = log_content.find(']', begin) 
        troubled_report = log_content[begin:end]
        #print(troubled_report)

        cmd = 'touch %s' % troubled_report
        #print('Executing [%s]...' % cmd)
        os.system(cmd)
                
        for proc in psutil.process_iter():
                # check whether the process name matches
                if script_name in proc.name():
                        proc.kill()
                        #print('Executing [%s]...' % cmd)
        os.system(cmd)
        os.system('cd /home/mayank/libtech/src/scripts && nohup python3 APPI_meebhoomi_gram1b.py TestSuite.test_fetch_appi_report &')
