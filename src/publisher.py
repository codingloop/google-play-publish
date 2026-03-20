import logging
from typing import Any

from exception import PublishError
from utils import get_absolute_path

logger = logging.getLogger(__name__)


class PlayStorePublisher:

    def __init__(self, config: dict, service: Any):
        self.config = config
        self.service = service
        self.edit_id = None

    @staticmethod
    def execute(config: dict, service: Any):
        publisher = PlayStorePublisher(config, service)

        logger.info("Creating edit session for %s", config.get('package_name'))
        publisher.create_edit()

        logger.info("Uploading app bundle")
        publisher.upload_aab()

        logger.info("Updating release on track: %s", config.get('track'))
        publisher.update_release()

        logger.info("Committing edit")
        publisher.commit_edit()

        logger.info("Successfully published to Google Play")

    @property
    def package_name(self) -> str:
        return self.config['package_name']

    def create_edit(self):
        try:
            request = self.service.edits().insert(body={}, packageName=self.package_name)
            res = request.execute()
            self.edit_id = res['id']
            logger.debug("Edit session created with ID: %s", self.edit_id)
        except Exception as e:
            raise PublishError(f"Failed to create edit session: {e}") from e

    def upload_aab(self):
        app_location = get_absolute_path(self.config['app_file_path'])
        logger.debug("Uploading AAB from: %s", app_location)
        try:
            request = self.service.edits().bundles().upload(
                packageName=self.package_name,
                editId=self.edit_id,
                media_body=app_location,
                uploadType="media",
                media_mime_type="application/octet-stream"
            )
            res = request.execute()
            logger.debug("Uploaded AAB version code: %s", res.get('versionCode'))
        except Exception as e:
            raise PublishError(f"Failed to upload app bundle: {e}") from e

    def update_release(self):
        try:
            res = self.service.edits().tracks().update(
                editId=self.edit_id,
                track=self.config['track'],
                packageName=self.package_name,
                body={
                    'releases': [{
                        'name': self.config['release_name'],
                        'versionCodes': [self.config['version_code']],
                        'status': self.config['release_status'],
                        'releaseNotes': self.config['release_notes'],
                    }]
                }
            ).execute()
            logger.debug("Track update response: %s", res)
        except Exception as e:
            raise PublishError(f"Failed to update release track: {e}") from e

    def commit_edit(self):
        try:
            self.service.edits().commit(
                editId=self.edit_id,
                packageName=self.package_name
            ).execute()
            logger.debug("Edit committed successfully")
        except Exception as e:
            raise PublishError(f"Failed to commit edit: {e}") from e
