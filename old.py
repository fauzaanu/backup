import os
import time
import psutil
import zipfile
import shutil
import watchdog.events
import watchdog.observers
import schedule
from dotenv import load_dotenv
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# Load environment variables
load_dotenv()

# Set constants from environment
BACKUP_PATH = os.getenv('BACKUP_PATH')
BACKUP_TARGET_PATH = os.getenv('BACKUP_TARGET_PATH')
BACKUP_TARGET_PASSWORD = os.getenv('BACKUP_TARGET_PASSWORD')[:16]

def zip_and_encrypt(directory, zipfile_name, encrypted_zipfile_name):
    with zipfile.ZipFile(zipfile_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory):
            for file in files:
                zipf.write(os.path.join(root, file))
                
    cipher = AES.new(BACKUP_TARGET_PASSWORD.encode(), AES.MODE_CBC)
    
    with open(zipfile_name, 'rb') as f_input, open(encrypted_zipfile_name, 'wb') as f_output:
        plaintext = f_input.read()
        ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
        f_output.write(cipher.iv)
        f_output.write(ciphertext)

    os.remove(zipfile_name)  # remove unencrypted zip file

def backup_when_idle():
    while True:
        cpu_usage = psutil.cpu_percent()
        
        if cpu_usage < 20:
            for folder in os.listdir(BACKUP_PATH):
                folder_path = os.path.join(BACKUP_PATH, folder)

                if os.path.isdir(folder_path):
                    zipfile_name = f"{folder_path}.zip"
                    encrypted_zipfile_name = f"{folder_path}.enc.zip"

                    zip_and_encrypt(folder_path, zipfile_name, encrypted_zipfile_name)
                    shutil.move(encrypted_zipfile_name, BACKUP_TARGET_PATH)
        else:
            time.sleep(30)  # wait for 30 seconds before checking again

class FileChangeHandler(watchdog.events.FileSystemEventHandler):
    def __init__(self, *args, **kwargs):
        self.change_size = 0
        super().__init__(*args, **kwargs)

    def on_modified(self, event):
        file_stats = os.stat(event.src_path)
        self.change_size += file_stats.st_size

        if self.change_size > 100_000_000: # Change size > 100MB
            schedule.every(1).minutes.do(backup_when_idle)
            self.change_size = 0  # Reset change size

def main():
    event_handler = FileChangeHandler()
    observer = watchdog.observers.Observer()

    observer.schedule(event_handler, path=BACKUP_PATH, recursive=True)
    observer.start()

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()

    observer.join()

if __name__ == "__main__":
    main()
