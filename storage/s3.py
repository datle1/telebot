from storage.storage import Storage


class S3Storage(Storage):

    def __init__(self):
        pass

    def user_exist(self, user_name):
        pass
        
    def insert_user(self, user_name):
        pass

    def delete_user(self, user_name):
        pass

    def get_all_users(self):
        pass

    def get_all_jobs(self):
        pass
    
    def insert_job(self, days_str, message, times_str, groups):
        pass

    def delete_job(self, id):
        pass

    def get_job_status(self, id):
        pass

    def switch_job(self, new_status, id):
        pass