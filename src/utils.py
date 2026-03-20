import logging
import os
import shutil
import subprocess
import sys

from google.oauth2 import service_account

from exception import CredentialsError

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/androidpublisher']


def stop_exec(message: str = None):
    if message:
        logger.error(message)
    sys.exit(1)


def get_absolute_path(relative_path: str) -> str:
    workspace = os.environ.get('GITHUB_WORKSPACE', '')
    if not workspace:
        raise EnvironmentError("GITHUB_WORKSPACE environment variable is not set")
    return f"{workspace}/{relative_path}"


def get_google_credentials(encrypted_file: str, decryption_pwd: str) -> service_account.Credentials:
    """
    Decrypts a GPG-encrypted service account file and returns Google credentials.

    The passphrase is passed via stdin to GPG to avoid exposing it in the process list.
    """
    tmp_dir = "tmp"
    os.makedirs(tmp_dir, exist_ok=True)
    try:
        encrypted_path = os.path.join(tmp_dir, "secret_file.asc")
        decrypted_path = os.path.join(tmp_dir, "client_secrets.json")

        with open(encrypted_path, "w") as f:
            f.write(encrypted_file)

        result = subprocess.run(
            ['gpg', '-d', '--passphrase-fd', '0', '--batch', '--yes', encrypted_path],
            input=decryption_pwd.encode(),
            capture_output=True
        )

        if result.returncode != 0:
            raise CredentialsError(
                f"Failed to decrypt service account file.\n"
                f"GPG error: {result.stderr.decode().strip()}"
            )

        with open(decrypted_path, "wb") as f:
            f.write(result.stdout)

        credentials = service_account.Credentials.from_service_account_file(
            decrypted_path, scopes=SCOPES
        )
        return credentials

    except CredentialsError:
        raise
    except Exception as e:
        raise CredentialsError(f"Unexpected error loading credentials: {e}") from e
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
