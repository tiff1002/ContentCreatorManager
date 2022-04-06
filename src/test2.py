'''
Created on Mar 15, 2022

@author: tiff
'''
import threading

class ThreadTester(threading.Thread):
    def __init__(self, var1, var2):
        super().__init__()
        lock = threading.Lock()
        with lock:
            var1 = 10
            var2 = 20
    
    def run(self):
        self.var1 = 10
        self.var2 = 20
        