'''
Created on Mar 15, 2022

@author: tiff
'''
import threading

var1 = 1
var2 = 2
lock = threading.Lock()

def thread_func(var1, var2, lock):
    with lock:
        var1 = 10
        var2 = 20

thread = threading.Thread(target=thread_func(var1, var2, lock))
   
print(var1)
print(var2)

thread.start()
while thread.is_alive():
    print('running')
print(var1)
print(var2)