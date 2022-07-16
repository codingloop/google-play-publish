import googleapiclient.discovery

from publisher import PlayStorePublisher
from read_config import read_config
from utils import stop_exec, get_google_credentials


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
    import sys
    print(sys.argv)
    # main(*sys.argv)
    import os
    print(os.environ)
    # p1 = os.environ['INPUT_CONFIG_FILE']
    # p2 = os.environ['INPUT_PLAYSTORE_ENCRYPTED_FILE']
    # p3 = os.environ['INPUT_PLAYSTORE_DECRYPTION_PWD']
    # main(p1, p2, p3)
