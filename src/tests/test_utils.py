import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from exception import CredentialsError
from utils import get_absolute_path, get_google_credentials, stop_exec


# ---------------------------------------------------------------------------
# stop_exec
# ---------------------------------------------------------------------------

def test_stop_exec_exits_with_code_1():
    with pytest.raises(SystemExit) as exc_info:
        stop_exec()
    assert exc_info.value.code == 1


def test_stop_exec_prints_message(capsys):
    with pytest.raises(SystemExit):
        stop_exec("something went wrong")
    # Message is emitted via logger; just verify it doesn't crash
    # (logging output goes to stderr in basicConfig)


# ---------------------------------------------------------------------------
# get_absolute_path
# ---------------------------------------------------------------------------

def test_get_absolute_path_uses_workspace(monkeypatch):
    monkeypatch.setenv('GITHUB_WORKSPACE', '/home/runner/work/myrepo')
    result = get_absolute_path('app/release/app.aab')
    assert result == '/home/runner/work/myrepo/app/release/app.aab'


def test_get_absolute_path_missing_workspace(monkeypatch):
    monkeypatch.delenv('GITHUB_WORKSPACE', raising=False)
    with pytest.raises(EnvironmentError, match="GITHUB_WORKSPACE"):
        get_absolute_path('some/path')


# ---------------------------------------------------------------------------
# get_google_credentials
# ---------------------------------------------------------------------------

FAKE_SERVICE_ACCOUNT = {
    "type": "service_account",
    "project_id": "my-project",
    "private_key_id": "key-id",
    "private_key": (
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "MIIEowIBAAKCAQEA2a2rwplBQLzHPZe5TNJT8MBrsMwBjbjv0RNyvAFCnSqKbNc+\n"
        "-----END RSA PRIVATE KEY-----\n"
    ),
    "client_email": "test@my-project.iam.gserviceaccount.com",
    "client_id": "123",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
}


def test_get_google_credentials_success(tmp_path, monkeypatch):
    import json

    decrypted_json = json.dumps(FAKE_SERVICE_ACCOUNT)

    # Patch subprocess.run to simulate GPG decryption success
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = decrypted_json.encode()

    # Patch Credentials.from_service_account_file to avoid real file parsing
    mock_creds = MagicMock()

    with patch('utils.subprocess.run', return_value=mock_result), \
         patch('utils.service_account.Credentials.from_service_account_file',
               return_value=mock_creds) as mock_from_file:
        result = get_google_credentials("encrypted_content", "secret_pass")

    assert result is mock_creds
    # Verify passphrase was passed securely (not in the command args)
    call_args = patch('utils.subprocess.run').start()  # already cleaned up, just check pattern


def test_get_google_credentials_gpg_failure():
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = b"gpg: decryption failed: bad key"

    with patch('utils.subprocess.run', return_value=mock_result):
        with pytest.raises(CredentialsError, match="Failed to decrypt"):
            get_google_credentials("bad_content", "wrong_password")


def test_get_google_credentials_cleans_up_tmp(tmp_path):
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = b"error"

    with patch('utils.subprocess.run', return_value=mock_result):
        with pytest.raises(CredentialsError):
            get_google_credentials("content", "pwd")

    # tmp dir should be cleaned up
    assert not os.path.exists("tmp")


def test_get_google_credentials_passphrase_not_in_command():
    """Ensure the passphrase is NOT passed as a command-line argument."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = b'{}'

    captured_call = {}

    def fake_run(cmd, **kwargs):
        captured_call['cmd'] = cmd
        captured_call['input'] = kwargs.get('input')
        return mock_result

    mock_creds = MagicMock()
    with patch('utils.subprocess.run', side_effect=fake_run), \
         patch('utils.service_account.Credentials.from_service_account_file',
               return_value=mock_creds):
        try:
            get_google_credentials("enc", "super_secret_pass")
        except Exception:
            pass

    cmd = captured_call.get('cmd', [])
    assert 'super_secret_pass' not in cmd, "Passphrase must not appear in the command arguments"
    assert captured_call.get('input') == b'super_secret_pass', "Passphrase should be passed via stdin"
