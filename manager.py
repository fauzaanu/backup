import os
import zipfile
import logging
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

class BackupManager:
    def __init__(self, backup_path, backup_target_path, backup_target_password):
        self.backup_path = backup_path
        self.backup_target_path = backup_target_path
        self.backup_target_password = backup_target_password
        logging.basicConfig(filename='backup_manager.log', level=logging.INFO)

    def zipdir(self, directory, zip_filename):
        """Compress directory into a zip file."""
        try:
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(directory):
                    for file in files:
                        zipf.write(os.path.join(root, file))
            logging.info(f"Compressed directory {directory} into zip file {zip_filename}.")
        except Exception as e:
            logging.error(f"An error occurred while compressing directory {directory}: {str(e)}")

    def encrypt_file(self, input_filename, output_filename):
        """Encrypt the input file using the provided key and write to output file."""
        try:
            cipher = AES.new(self.backup_target_password.encode(), AES.MODE_CBC)

            with open(input_filename, 'rb') as f_input, open(output_filename, 'wb') as f_output:
                plaintext = f_input.read()
                ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
                f_output.write(cipher.iv)
                f_output.write(ciphertext)
            logging.info(f"Encrypted file {input_filename} into {output_filename}.")
        except Exception as e:
            logging.error(f"An error occurred while encrypting file {input_filename}: {str(e)}")

    def backup(self):
        """Backup each subdirectory of BACKUP_PATH by compressing and encrypting it."""
        try:
            for folder in os.listdir(self.backup_path):
                directory_path = os.path.join(self.backup_path, folder)

                if os.path.isdir(directory_path):
                    zip_filename = directory_path + '.zip'
                    encrypted_zip_filename = directory_path + '.enc.zip'
                    self.zipdir(directory_path, zip_filename)
                    self.encrypt_file(zip_filename, encrypted_zip_filename)
                    os.remove(zip_filename)  # remove unencrypted zip file
                    logging.info(f"Backed up directory {directory_path}.")
        except Exception as e:
            logging.error(f"An error occurred during backup: {str(e)}")
