from typing import Any


class PlayStorePublisher:

    def __int__(self, config: dict, service: Any):
        self.config = config
        self.service = service
        self.edit_id = None

    @staticmethod
    def execute(config: dict, service: Any):
        publisher = PlayStorePublisher(config, service)
        publisher.create_edit()
        publisher.upload_aab()
        publisher.update_release()
        publisher.commit_edit()

    @property
    def package_name(self):
        return self.config['package_name']

    def create_edit(self):
        request = self.service.edits().insert(body={}, packageName=self.package_name)
        res = request.execute()
        self.edit_id = res['id']

    def upload_aab(self):
        request = self.service.edits().bundles().upload(packageName=self.package_name, editId=self.edit_id,
                                                        media_body=self.config['app_file_path'], uploadType="media",
                                                        media_mime_type="application/octet-stream")
        request.execute()

    def update_release(self):
        res = self.service.edits().tracks().update(
            editId=self.edit_id,
            track=self.config['track'],
            packageName=self.package_name,
            body={u'releases': [{
                u'name': self.config['release_name'],
                u'versionCodes': [self.config['version_code']],
                u'status': self.config['release_status'],
                u'releaseNotes': self.config['release_notes']
            }]}).execute()

        print(res)

    def commit_edit(self):
        self.service.edits().commit(editId=self.edit_id, packageName=self.package_name).execute()

