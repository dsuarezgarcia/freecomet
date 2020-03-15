# -*- encoding: utf-8 -*-

'''
    The threads module.
'''


import threading
import ctypes


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	ThreadWithException                                                       #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class ThreadWithException(threading.Thread):

    '''
        The ThreadWithException class.
    '''
 
    ''' Initialization method. '''
    def __init__(self, target, args): 

        threading.Thread.__init__(self, target=target, args=args) 
           
    def get_id(self): 
  
        # Returns id of the respective thread 
        if hasattr(self, '_thread_id'): 
            return self.thread_id

        for id, thread in threading.active.items(): 
            if thread is self: 
                return id
   
    def raise_exception(self):

        thread_id = self.get_id() 
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 
              ctypes.py_object(SystemExit)) 
        if res > 1: 
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0) 
 

