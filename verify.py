import os
import zipfile
import filecmp
import shutil
import logging
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

class BackupVerifier:
    def __init__(self, backup_target_path, backup_target_password):
        self.backup_target_path = backup_target_path
        self.backup_target_password = backup_target_password
        logging.basicConfig(filename='backup_verifier.log', level=logging.INFO)

    def decrypt_file(self, input_filename, output_filename):
        try:
            with open(input_filename, 'rb') as f_input, open(output_filename, 'wb') as f_output:
                iv = f_input.read(16)
                cipher = AES.new(self.backup_target_password.encode(), AES.MODE_CBC, iv=iv)
                ciphertext = f_input.read()
                plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
                f_output.write(plaintext)
        except Exception as e:
            logging.error(f"An error occurred while decrypting the file: {str(e)}")
            raise e

    def verify(self):
        try:
            for filename in os.listdir(self.backup_target_path):
                if filename.endswith('.enc.zip'):
                    encrypted_zip_filename = os.path.join(self.backup_target_path, filename)
                    zip_filename = encrypted_zip_filename.replace('.enc.zip', '.zip')
                    directory_path = zip_filename.replace('.zip', '')

                    self.decrypt_file(encrypted_zip_filename, zip_filename)

                    with zipfile.ZipFile(zip_filename, 'r') as zipf:
                        zipf.extractall(directory_path)

                    original_directory_path = os.path.join(self.backup_target_path, filename.replace('.enc.zip', ''))
                    comparison = filecmp.dircmp(directory_path, original_directory_path)

                    if comparison.left_only or comparison.right_only or comparison.diff_files:
                        logging.error(f"Backup verification failed for {filename}")
                        return False

                    os.remove(zip_filename)
                    shutil.rmtree(directory_path)

            logging.info("Backup verification completed successfully.")
            return True

        except Exception as e:
            logging.error(f"An error occurred during backup verification: {str(e)}")
            return False
