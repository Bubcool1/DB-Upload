import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
from dotenv import load_dotenv

load_dotenv()
# NOTE: IF THE FOLDER IS OPEN THEN THERE IS A PERMISSIONS ERROR CLOSE THAT FOLDER THAT WILL FIX IT.
class MonitorFolder(FileSystemEventHandler):
    
    def on_created(self, event):
        print(event.src_path, event.event_type)
        url=os.getenv('URL')
        files = event.src_path
        assert os.path.isfile(files)
        file={'file': open(files,'rb')}
        headers = {'token': os.getenv('TOKEN')}
        r=requests.post(url,files=file, headers=headers)
        print(r.text.strip() + ' - Code ' + str(r.status_code))
                  
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