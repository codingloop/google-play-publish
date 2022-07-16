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
        print(e.__traceback__)
        stop_exec()


if __name__ == '__main__':
    import os
    p1 = os.environ['config_file']
    p2 = os.environ['playstore_encrypted_file']
    p3 = os.environ['playstore_decryption_pwd']
    # GITHUB_WORKSPACE
    main(p1, p2, p3)
