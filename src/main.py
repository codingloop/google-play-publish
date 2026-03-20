import logging
import os
import sys

import googleapiclient.discovery

from exception import ConfigValidationError, CredentialsError, PublishError
from publisher import PlayStorePublisher
from read_config import read_config
from utils import get_absolute_path, get_google_credentials

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S',
)
logger = logging.getLogger(__name__)


def main(config_file: str, playstore_encrypted_file: str, playstore_decryption_pwd: str):
    try:
        logger.info("Reading config file: %s", config_file)
        config = read_config(config_file)

        logger.info("Loading Google Play credentials")
        creds = get_google_credentials(playstore_encrypted_file, playstore_decryption_pwd)

        logger.info("Building Android Publisher API service")
        service = googleapiclient.discovery.build('androidpublisher', 'v3', credentials=creds)

        logger.info("Starting publish workflow")
        PlayStorePublisher.execute(config, service)

        logger.info("Publish completed successfully")

    except ConfigValidationError as e:
        logger.error("Configuration error: %s", e)
        sys.exit(1)
    except CredentialsError as e:
        logger.error("Credentials error: %s", e)
        sys.exit(1)
    except PublishError as e:
        logger.error("Publish error: %s", e)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        sys.exit(1)


if __name__ == '__main__':
    config_file = os.environ.get('config_file')
    encrypted_file = os.environ.get('playstore_encrypted_file')
    decryption_pwd = os.environ.get('playstore_decryption_pwd')

    missing_vars = [
        name for name, val in [
            ('config_file', config_file),
            ('playstore_encrypted_file', encrypted_file),
            ('playstore_decryption_pwd', decryption_pwd),
        ] if not val
    ]
    if missing_vars:
        logger.error("Missing required environment variables: %s", ', '.join(missing_vars))
        sys.exit(1)

    config_file = get_absolute_path(config_file)
    main(config_file, encrypted_file, decryption_pwd)
