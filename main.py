import os
import time
import logging
import schedule
from dotenv import load_dotenv
from manager import BackupManager
from monitor import SystemMonitor, FileMonitor
from rotate import BackupRotator
from verify import BackupVerifier
from notify import UserNotifier

# Load environment variables
load_dotenv()

# Set constants from environment
BACKUP_PATH = os.getenv('BACKUP_PATH')
BACKUP_TARGET_PATH = os.getenv('BACKUP_TARGET_PATH')
BACKUP_TARGET_PASSWORD = os.getenv('BACKUP_TARGET_PASSWORD')[:16]
RETENTION_PERIOD = os.getenv('RETENTION_PERIOD')  # get retention period from environment variables

# Initialize components
backup_manager = BackupManager(BACKUP_PATH, BACKUP_TARGET_PATH, BACKUP_TARGET_PASSWORD)
system_monitor = SystemMonitor()
file_monitor = FileMonitor(BACKUP_PATH)
backup_rotator = BackupRotator(BACKUP_TARGET_PATH, RETENTION_PERIOD)
backup_verifier = BackupVerifier(BACKUP_TARGET_PATH, BACKUP_TARGET_PASSWORD)
user_notifier = UserNotifier()

logging.basicConfig(filename='main.log', level=logging.INFO)

def main():
    # Start the file monitor and system monitor
    file_monitor.start()
    system_monitor.start()
    user_notifier.notify("File monitor and system monitor started.")

    try:
        while True:
            # Check if a backup is needed
            if file_monitor.is_backup_needed() and system_monitor.is_system_idle():
                # Perform the backup
                backup_manager.backup()
                user_notifier.notify("Backup performed.")

                # Verify the backup
                if not backup_verifier.verify():
                    user_notifier.notify("Backup verification failed!")
                    logging.error("Backup verification failed!")
                else:
                    user_notifier.notify("Backup verification successful.")

                # Rotate old backups
                backup_rotator.rotate()
                user_notifier.notify("Old backups rotated.")

            # Sleep for a while
            time.sleep(60)

    except KeyboardInterrupt:
        # Stop the file monitor and system monitor
        file_monitor.stop()
        system_monitor.stop()
        user_notifier.notify("File monitor and system monitor stopped due to KeyboardInterrupt.")
        logging.info("Stopped file monitor and system monitor due to KeyboardInterrupt.")

    except Exception as e:
        user_notifier.notify(f"An error occurred: {str(e)}")
        logging.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
