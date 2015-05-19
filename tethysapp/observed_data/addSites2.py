from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from threading import Thread
from Queue import Queue, Empty as QueueEmpty
from .model import spatial_engine
import addSites,os
from .utilities import get_persistent_store_engine
import multiprocessing,logging
import time


# logger = multiprocessing.log_to_stderr()
# logger.setLevel(logging.DEBUG)
engine = get_persistent_store_engine('sites_db')

def worker(num):
    name = multiprocessing.current_process().name
    print name, 'Starting'

    item=num
    path = os.path.join(os.path.dirname(__file__),'lib','test')
    filePath = path + '/' + item
    result = addSites.readSites(filePath)
    if(len(result)>0):
        
        DBSession = sessionmaker(bind=engine)
        db_session = DBSession()
        addSites.doSomethingWithResult(result,db_session)
        db_session.close()
  
    print name, 'Exiting'


all_items = addSites.files()
print len(all_items)
from multiprocessing import Pool

def add():
    pool = Pool(processes=16)
    x = pool.map_async(worker, all_items)
    pool.close()
    pool.join()



# def add():
#     jobs = []
#     for i in range(len(all_items)):
#         p = multiprocessing.Process(target=worker, args=(i,))
#         jobs.append(p)
#         p.start()

