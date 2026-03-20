import json
import logging
from json import JSONDecodeError

from exception import ConfigValidationError

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = [
    'package_name',
    'app_file_path',
    'track',
    'version_code',
    'release_name',
    'release_status',
    'release_notes',
]

VALID_TRACKS = {'production', 'beta', 'alpha', 'internal'}
VALID_STATUSES = {'draft', 'completed', 'halted', 'inProgress'}


def read_config(file_path: str) -> dict:
    try:
        with open(file_path) as f:
            data = json.load(f)
    except FileNotFoundError:
        raise ConfigValidationError(
            f"Config file not found: {file_path}"
        )
    except JSONDecodeError as e:
        raise ConfigValidationError(
            f"Config file is not valid JSON: {e}"
        )

    _validate_config(data)
    return data


def _validate_config(config: dict):
    missing = [field for field in REQUIRED_FIELDS if field not in config]
    if missing:
        raise ConfigValidationError(
            f"Config is missing required fields: {', '.join(missing)}"
        )

    track = config.get('track', '')
    if track not in VALID_TRACKS:
        raise ConfigValidationError(
            f"Invalid track '{track}'. Must be one of: {', '.join(sorted(VALID_TRACKS))}"
        )

    status = config.get('release_status', '')
    if status not in VALID_STATUSES:
        raise ConfigValidationError(
            f"Invalid release_status '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}"
        )

    version_code = config.get('version_code')
    if not isinstance(version_code, int) or version_code <= 0:
        raise ConfigValidationError(
            f"version_code must be a positive integer, got: {version_code!r}"
        )

    release_notes = config.get('release_notes', [])
    if not isinstance(release_notes, list):
        raise ConfigValidationError("release_notes must be a list")
    for i, note in enumerate(release_notes):
        if not isinstance(note, dict) or 'language' not in note or 'text' not in note:
            raise ConfigValidationError(
                f"release_notes[{i}] must have 'language' and 'text' fields"
            )

    logger.info("Config validation passed for package: %s", config.get('package_name'))
