import os
import sys

from google.oauth2 import service_account


def stop_exec(message: str = None):
    if message:
        print(message)

    sys.exit(5)


def get_google_credentials(encrypted_file: str, decryption_pwd: str):
    SCOPES = ['https://www.googleapis.com/auth/androidpublisher']
    os.system(f"gpg -d --passphrase {decryption_pwd} --batch {encrypted_file} > tmp/keystore.jks")
    credentials = service_account.Credentials.from_service_account_file("tmp/keystore.jks", scopes=SCOPES)
    os.removedirs("tmp")
    return credentials




