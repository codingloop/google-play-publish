import googleapiclient.discovery

from publisher import PlayStorePublisher
from read_config import read_config
from utils import stop_exec, get_google_credentials, get_absolute_path


def main(config_file, playstore_encrypted_file, playstore_decryption_pwd):
    try:
        print("Reading config file")
        config = read_config(config_file)

        print("Reading google creds")
        creds = get_google_credentials(playstore_encrypted_file, playstore_decryption_pwd)

        print("Creating API service")
        service = googleapiclient.discovery.build('androidpublisher', 'v3', credentials=creds)

        print("Creating new draft release")
        PlayStorePublisher.execute(config, service)

    except Exception as e:
        print(e.args)
        stop_exec()


if __name__ == '__main__':
    import os
    p1 = os.environ['config_file']
    p1 = get_absolute_path(p1)
    p2 = os.environ['playstore_encrypted_file']
    p3 = os.environ['playstore_decryption_pwd']
    main(p1, p2, p3)
