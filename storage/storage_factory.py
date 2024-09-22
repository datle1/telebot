from storage.s3 import S3Storage
from storage.sqlite import SqliteStorage


class StorageFactory():
    @staticmethod
    def get_storage(type='sqlite'):
        storage_type = {
            "sqlite": SqliteStorage,
            # "s3": S3Storage
        }

        return storage_type[type]()