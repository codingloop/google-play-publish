import sys

import googleapiclient.discovery

from publisher import PlayStorePublisher
from read_config import read_config
from utils import stop_exec, get_google_credentials, print_to_github_action


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
    import os
    print(os.environ)
    # main(*sys.argv)
