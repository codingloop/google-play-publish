import json
import os
import tempfile

import pytest

from exception import ConfigValidationError
from read_config import read_config

VALID_CONFIG = {
    "package_name": "com.example.myapp",
    "app_file_path": "app/build/outputs/bundle/release/app-release.aab",
    "track": "internal",
    "version_code": 42,
    "release_name": "2.1.0",
    "release_status": "completed",
    "release_notes": [
        {"language": "en-US", "text": "Bug fixes."}
    ],
}


def write_config(data: dict) -> str:
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(data, f)
    f.close()
    return f.name


def test_valid_config():
    path = write_config(VALID_CONFIG)
    try:
        result = read_config(path)
        assert result['package_name'] == 'com.example.myapp'
        assert result['version_code'] == 42
    finally:
        os.unlink(path)


def test_file_not_found():
    with pytest.raises(ConfigValidationError, match="Config file not found"):
        read_config("/nonexistent/path/config.json")


def test_invalid_json(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{ not valid json }")
    with pytest.raises(ConfigValidationError, match="not valid JSON"):
        read_config(str(bad_file))


@pytest.mark.parametrize("missing_field", [
    "package_name", "app_file_path", "track", "version_code",
    "release_name", "release_status", "release_notes",
])
def test_missing_required_field(missing_field):
    config = {**VALID_CONFIG}
    del config[missing_field]
    path = write_config(config)
    try:
        with pytest.raises(ConfigValidationError, match="missing required fields"):
            read_config(path)
    finally:
        os.unlink(path)


@pytest.mark.parametrize("track", ["production", "beta", "alpha", "internal"])
def test_valid_tracks(track):
    config = {**VALID_CONFIG, "track": track}
    path = write_config(config)
    try:
        result = read_config(path)
        assert result['track'] == track
    finally:
        os.unlink(path)


def test_invalid_track():
    config = {**VALID_CONFIG, "track": "staging"}
    path = write_config(config)
    try:
        with pytest.raises(ConfigValidationError, match="Invalid track"):
            read_config(path)
    finally:
        os.unlink(path)


@pytest.mark.parametrize("status", ["draft", "completed", "inProgress", "halted"])
def test_valid_statuses(status):
    config = {**VALID_CONFIG, "release_status": status}
    path = write_config(config)
    try:
        result = read_config(path)
        assert result['release_status'] == status
    finally:
        os.unlink(path)


def test_invalid_release_status():
    config = {**VALID_CONFIG, "release_status": "published"}
    path = write_config(config)
    try:
        with pytest.raises(ConfigValidationError, match="Invalid release_status"):
            read_config(path)
    finally:
        os.unlink(path)


@pytest.mark.parametrize("bad_version", [0, -1, "1", 1.5, None])
def test_invalid_version_code(bad_version):
    config = {**VALID_CONFIG, "version_code": bad_version}
    path = write_config(config)
    try:
        with pytest.raises(ConfigValidationError, match="version_code"):
            read_config(path)
    finally:
        os.unlink(path)


def test_release_notes_not_a_list():
    config = {**VALID_CONFIG, "release_notes": "some notes"}
    path = write_config(config)
    try:
        with pytest.raises(ConfigValidationError, match="release_notes must be a list"):
            read_config(path)
    finally:
        os.unlink(path)


def test_release_notes_missing_fields():
    config = {**VALID_CONFIG, "release_notes": [{"language": "en-US"}]}
    path = write_config(config)
    try:
        with pytest.raises(ConfigValidationError, match="'language' and 'text'"):
            read_config(path)
    finally:
        os.unlink(path)


def test_multiple_release_notes():
    config = {**VALID_CONFIG, "release_notes": [
        {"language": "en-US", "text": "English notes"},
        {"language": "fr-FR", "text": "French notes"},
    ]}
    path = write_config(config)
    try:
        result = read_config(path)
        assert len(result['release_notes']) == 2
    finally:
        os.unlink(path)
