from unittest.mock import MagicMock, call, patch

import pytest

from exception import PublishError
from publisher import PlayStorePublisher

VALID_CONFIG = {
    "package_name": "com.example.myapp",
    "app_file_path": "app/build/outputs/bundle/release/app-release.aab",
    "track": "internal",
    "version_code": 42,
    "release_name": "2.1.0",
    "release_status": "completed",
    "release_notes": [{"language": "en-US", "text": "Bug fixes."}],
}


def make_service():
    """Build a fully mocked Android Publisher API service."""
    service = MagicMock()
    # Chain: service.edits().insert(...).execute()
    service.edits.return_value.insert.return_value.execute.return_value = {'id': 'edit-123'}
    service.edits.return_value.bundles.return_value.upload.return_value.execute.return_value = {
        'versionCode': 42
    }
    service.edits.return_value.tracks.return_value.update.return_value.execute.return_value = {
        'track': 'internal'
    }
    service.edits.return_value.commit.return_value.execute.return_value = {}
    return service


# ---------------------------------------------------------------------------
# execute (full happy path)
# ---------------------------------------------------------------------------

def test_execute_calls_all_stages(monkeypatch):
    monkeypatch.setenv('GITHUB_WORKSPACE', '/workspace')
    service = make_service()
    PlayStorePublisher.execute(VALID_CONFIG, service)

    # create_edit
    service.edits.return_value.insert.assert_called_once_with(
        body={}, packageName='com.example.myapp'
    )
    # upload_aab
    service.edits.return_value.bundles.return_value.upload.assert_called_once()
    # update_release
    service.edits.return_value.tracks.return_value.update.assert_called_once()
    # commit
    service.edits.return_value.commit.assert_called_once()


# ---------------------------------------------------------------------------
# package_name property
# ---------------------------------------------------------------------------

def test_package_name():
    pub = PlayStorePublisher(VALID_CONFIG, MagicMock())
    assert pub.package_name == 'com.example.myapp'


# ---------------------------------------------------------------------------
# create_edit
# ---------------------------------------------------------------------------

def test_create_edit_stores_edit_id():
    service = make_service()
    pub = PlayStorePublisher(VALID_CONFIG, service)
    pub.create_edit()
    assert pub.edit_id == 'edit-123'


def test_create_edit_raises_publish_error_on_api_failure():
    service = MagicMock()
    service.edits.return_value.insert.return_value.execute.side_effect = Exception("API error")
    pub = PlayStorePublisher(VALID_CONFIG, service)
    with pytest.raises(PublishError, match="Failed to create edit session"):
        pub.create_edit()


# ---------------------------------------------------------------------------
# upload_aab
# ---------------------------------------------------------------------------

def test_upload_aab_uses_absolute_path(monkeypatch):
    monkeypatch.setenv('GITHUB_WORKSPACE', '/workspace')
    service = make_service()
    pub = PlayStorePublisher(VALID_CONFIG, service)
    pub.edit_id = 'edit-123'
    pub.upload_aab()

    upload_call = service.edits.return_value.bundles.return_value.upload
    _, kwargs = upload_call.call_args
    assert kwargs['media_body'] == '/workspace/app/build/outputs/bundle/release/app-release.aab'


def test_upload_aab_raises_publish_error_on_failure(monkeypatch):
    monkeypatch.setenv('GITHUB_WORKSPACE', '/workspace')
    service = MagicMock()
    service.edits.return_value.bundles.return_value.upload.return_value.execute.side_effect = (
        Exception("upload failed")
    )
    pub = PlayStorePublisher(VALID_CONFIG, service)
    pub.edit_id = 'edit-123'
    with pytest.raises(PublishError, match="Failed to upload app bundle"):
        pub.upload_aab()


# ---------------------------------------------------------------------------
# update_release
# ---------------------------------------------------------------------------

def test_update_release_sends_correct_body():
    service = make_service()
    pub = PlayStorePublisher(VALID_CONFIG, service)
    pub.edit_id = 'edit-123'
    pub.update_release()

    update_call = service.edits.return_value.tracks.return_value.update
    _, kwargs = update_call.call_args
    body = kwargs['body']
    assert body['releases'][0]['versionCodes'] == [42]
    assert body['releases'][0]['status'] == 'completed'
    assert body['releases'][0]['name'] == '2.1.0'


def test_update_release_raises_publish_error_on_failure():
    service = MagicMock()
    service.edits.return_value.tracks.return_value.update.return_value.execute.side_effect = (
        Exception("track update failed")
    )
    pub = PlayStorePublisher(VALID_CONFIG, service)
    pub.edit_id = 'edit-123'
    with pytest.raises(PublishError, match="Failed to update release track"):
        pub.update_release()


# ---------------------------------------------------------------------------
# commit_edit
# ---------------------------------------------------------------------------

def test_commit_edit_calls_api():
    service = make_service()
    pub = PlayStorePublisher(VALID_CONFIG, service)
    pub.edit_id = 'edit-123'
    pub.commit_edit()
    service.edits.return_value.commit.assert_called_once_with(
        editId='edit-123', packageName='com.example.myapp'
    )


def test_commit_edit_raises_publish_error_on_failure():
    service = MagicMock()
    service.edits.return_value.commit.return_value.execute.side_effect = Exception("commit failed")
    pub = PlayStorePublisher(VALID_CONFIG, service)
    pub.edit_id = 'edit-123'
    with pytest.raises(PublishError, match="Failed to commit edit"):
        pub.commit_edit()
