import logging

class UserNotifier:
    def __init__(self):
        logging.basicConfig(filename='user_notifier.log', level=logging.INFO)

    def notify(self, message):
        """Notify the user."""
        try:
            print(message)
            logging.info(f"User notified with message: {message}")
        except Exception as e:
            logging.error(f"An error occurred while notifying the user: {str(e)}")
