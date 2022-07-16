import os
import shutil
import sys

from google.oauth2 import service_account


def stop_exec(message: str = None):
    if message:
        print(message)

    sys.exit(5)


def get_google_credentials(encrypted_file: str, decryption_pwd: str):
    SCOPES = ['https://www.googleapis.com/auth/androidpublisher']
    os.makedirs("tmp", exist_ok=True)
    with open("tmp/secret_file.asc", "w") as f:
        f.write(encrypted_file)
    os.system(f"gpg -d --passphrase {decryption_pwd} --batch tmp/secret_file.asc > tmp/client_secrets.json")
    credentials = service_account.Credentials.from_service_account_file("tmp/client_secrets.json", scopes=SCOPES)
    shutil.rmtree("tmp")
    return credentials




