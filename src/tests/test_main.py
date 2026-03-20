import sys
from unittest.mock import MagicMock, patch

import pytest

from exception import ConfigValidationError, CredentialsError, PublishError
from main import main


def test_main_happy_path():
    mock_config = {"package_name": "com.example.app"}
    mock_creds = MagicMock()
    mock_service = MagicMock()

    with patch('main.read_config', return_value=mock_config) as mock_read, \
         patch('main.get_google_credentials', return_value=mock_creds) as mock_creds_fn, \
         patch('main.googleapiclient.discovery.build', return_value=mock_service), \
         patch('main.PlayStorePublisher.execute') as mock_execute:
        main('config.json', 'enc_file', 'password')

    mock_read.assert_called_once_with('config.json')
    mock_creds_fn.assert_called_once_with('enc_file', 'password')
    mock_execute.assert_called_once_with(mock_config, mock_service)


def test_main_exits_on_config_error():
    with patch('main.read_config', side_effect=ConfigValidationError("bad config")):
        with pytest.raises(SystemExit) as exc_info:
            main('config.json', 'enc', 'pwd')
        assert exc_info.value.code == 1


def test_main_exits_on_credentials_error():
    with patch('main.read_config', return_value={}), \
         patch('main.get_google_credentials', side_effect=CredentialsError("bad creds")):
        with pytest.raises(SystemExit) as exc_info:
            main('config.json', 'enc', 'pwd')
        assert exc_info.value.code == 1


def test_main_exits_on_publish_error():
    with patch('main.read_config', return_value={}), \
         patch('main.get_google_credentials', return_value=MagicMock()), \
         patch('main.googleapiclient.discovery.build', return_value=MagicMock()), \
         patch('main.PlayStorePublisher.execute', side_effect=PublishError("upload failed")):
        with pytest.raises(SystemExit) as exc_info:
            main('config.json', 'enc', 'pwd')
        assert exc_info.value.code == 1


def test_main_exits_on_unexpected_error():
    with patch('main.read_config', side_effect=RuntimeError("unexpected")):
        with pytest.raises(SystemExit) as exc_info:
            main('config.json', 'enc', 'pwd')
        assert exc_info.value.code == 1
