import os
import time
import logging

class BackupRotator:
    def __init__(self, backup_target_path, retention_period=7):
        self.backup_target_path = backup_target_path
        self.retention_period = retention_period  # in days, default is 7 days


    def rotate(self):
        """Delete backups that are older than the retention period."""
        try:
            for filename in os.listdir(self.backup_target_path):
                file_path = os.path.join(self.backup_target_path, filename)
                if os.path.isfile(file_path):
                    file_age = time.time() - os.path.getmtime(file_path)
                    if file_age > self.retention_period * 24 * 60 * 60:  # Convert retention period to seconds
                        os.remove(file_path)
                        logging.info(f"Removed backup file {filename} due to exceeding retention period.")
        except Exception as e:
            logging.error(f"An error occurred during backup rotation: {str(e)}")
