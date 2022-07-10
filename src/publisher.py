from typing import Any


class PlayStorePublisher:

    def __int__(self, config: dict, service: Any):
        self.config = config
        self.service = service
        self.edit_id = None

    @staticmethod
    def execute():
        pass

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


