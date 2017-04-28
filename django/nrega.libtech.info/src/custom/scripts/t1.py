from queue import Queue
from threading import Thread
import threading
#import _thread as Thread
import time
import random
maxQueue=20 
def crawler(url_queue):
    while True:
        time.sleep(4)
        url = url_queue.get()  # if there is no url, this will wait
        name = threading.currentThread().getName()
        print("Thread: {0} start download {1} at time = {2} \n".format(name, url, time.strftime('%H:%M:%S')))
 
        #time.sleep(random.randint(2,6))
 
        print("Thread: {0} finish download {1} at time = {2} \n".format(name, url, time.strftime('%H:%M:%S')))
        url_queue.task_done()
 
 
def url_producer(url_queue):
    while True:
      if(url_queue.qsize() < 10):
        for i in range(10):
          name = threading.currentThread().getName()
          url="URL = %s " %str(i)
          print("Thread: {0} start put url {1} into url_queue[current size={2}] at time = {3} \n".format(name, url, url_queue.qsize(), time.strftime('%H:%M:%S')))
          url_queue.put(url)
          print("Thread: {0} finish put url {1} into url_queue[current size={2}]  at time = {3} \n".format(name, url, url_queue.qsize(), time.strftime('%H:%M:%S')))
      else:
        print("Queu is not empty")
        time.sleep(8)
 
 
def main2():
    max_urls_in_queue = maxQueue
    q = Queue(maxsize=max_urls_in_queue)
    q.qsize()
    print(q.qsize())
 
    thread_pool_size = 5
 
    print('Main: start crawler threads at {0}'.format(time.strftime('%H:%M:%S')))
    for i in range(thread_pool_size):
         t = Thread(name = 'Thread-' + str(i), target=crawler, args=(q, ))
         t.daemon = True
         t.start()
 
 
    print('Main: start producer threads at {0}'.format(time.strftime('%H:%M:%S')))
 
    urls1 = ['Domain-A-URL-' + str(i) for i in range(3)]
    # we also use 2 threads to fill the queue
    t1 = Thread(name = 'url_producer-23', target=url_producer, args=(q, ))
    t1.daemon = True
    t1.start()
 
 #   time.sleep(120) 
 #   urls2 = ['Domain-B-URL-' + str(i) for i in range(4)]
 #   t2 = Thread(name = 'url_producer-1', target=url_producer, args=(urls2, q))
 #   t2.start()
 
    q.join()       # block until all tasks are done
 
 
if __name__ == '__main__':
 
    main2()
