import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests

class MonitorFolder(FileSystemEventHandler):
    
    def on_created(self, event):
        print(event.src_path, event.event_type)
        url='http://127.0.0.1:5000/uploadData'
        file={'file': open(event.src_path,'rb')}
        r=requests.post(url,files=file)
                  
if __name__ == "__main__":
    src_path = sys.argv[1]
    
    event_handler=MonitorFolder()
    observer = Observer()
    observer.schedule(event_handler, path=src_path, recursive=True)
    print("Monitoring started")
    observer.start()
    try:
        while(True):
           time.sleep(1)
           
    except KeyboardInterrupt:
            observer.stop()
            observer.join()