import os
import psutil
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileMonitor:
    def __init__(self, backup_path):
        self.backup_path = backup_path
        self.change_size = 0
        self.observer = Observer()
        logging.basicConfig(filename='file_monitor.log', level=logging.INFO)

    def start(self):
        try:
            event_handler = self.FileChangeHandler(self)
            self.observer.schedule(event_handler, self.backup_path, recursive=True)
            self.observer.start()
            logging.info("File monitor started.")
        except Exception as e:
            logging.error(f"An error occurred while starting the file monitor: {str(e)}")

    def stop(self):
        self.observer.stop()
        self.observer.join()

    def is_backup_needed(self):
        return self.change_size > 100_000_000  # Change size > 100MB

    class FileChangeHandler(FileSystemEventHandler):
        def __init__(self, file_monitor):
            self.file_monitor = file_monitor

        def on_modified(self, event):
            try:
                file_stats = os.stat(event.src_path)
                self.file_monitor.change_size += file_stats.st_size
            except Exception as e:
                logging.error(f"An error occurred while monitoring file changes: {str(e)}")

class SystemMonitor:
    def __init__(self):
        self.cpu_usage = 0
        logging.basicConfig(filename='system_monitor.log', level=logging.INFO)

    def start(self):
        try:
            while True:
                self.cpu_usage = psutil.cpu_percent()
                time.sleep(60)  # Check CPU usage every minute
                logging.info(f"System monitor checked CPU usage: {self.cpu_usage}%.")
        except Exception as e:
            logging.error(f"An error occurred while monitoring system usage: {str(e)}")

    def is_system_idle(self):
        return self.cpu_usage < 20  # System is idle if CPU usage < 20%
