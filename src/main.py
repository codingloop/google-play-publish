import sys

from src.publisher import PlayStorePublisher
from src.read_config import read_config
from src.utils import stop_exec, get_google_credentials
import googleapiclient.discovery


def main(config_file, playstore_encrypted_file, playstore_decryption_pwd):
    try:
        config = read_config(config_file)
        creds = get_google_credentials(playstore_encrypted_file, playstore_decryption_pwd)
        service = googleapiclient.discovery.build('androidpublisher', 'v3', credentials=creds)
        PlayStorePublisher.execute(config, service)

    except Exception as e:
        print(e.args)
        stop_exec()


if __name__ == '__main__':
    main(*sys.argv)
