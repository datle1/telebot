from ast import literal_eval
import io
from storage.storage import Storage
import boto3
from io import BytesIO
import os

BUCKET_NAME = 'telebucket'
USER_FILE = 'data/users.txt'
JOB_FILE = 'data/jobs.txt'
AWS_SERVER_PUBLIC_KEY = os.getenv('AWS_SERVER_PUBLIC_KEY')
AWS_SERVER_SECRET_KEY = os.getenv('AWS_SERVER_SECRET_KEY')
AWS_SERVER_REGION = os.getenv('AWS_SERVER_REGION')

class S3Storage(Storage):

    def __init__(self):
        session = boto3.Session(
                aws_access_key_id=AWS_SERVER_PUBLIC_KEY,
                aws_secret_access_key=AWS_SERVER_SECRET_KEY,
                region_name=AWS_SERVER_REGION
            )
        self.s3_client = session.client('s3')
        self.users = self.get_user_data()
        self.jobs = self.get_job_data()

    def get_user_data(self):
        f = BytesIO()
        self.s3_client.download_fileobj(BUCKET_NAME, USER_FILE, f)
        data = f.getvalue().decode('utf-8')
        if len(data) > 0:
            return data.split('\n')
        return []

    def get_job_data(self):
        f = BytesIO()
        self.s3_client.download_fileobj(BUCKET_NAME, JOB_FILE, f)
        data = f.getvalue().decode('utf-8')
        if len(data) > 0:
            jobs = data.split('\n')
            result = []
            for job in jobs:
                result.append(literal_eval(job))
            return result
        return []

    def save_users(self):
        fo = io.BytesIO(b'\n'.join([bytes(item, 'utf-8') for item in self.users]))
        self.s3_client.upload_fileobj(fo, BUCKET_NAME, USER_FILE)

    def save_jobs(self):
        fo = io.BytesIO(b'\n'.join([bytes(str(item), 'utf-8') for item in self.jobs]))
        self.s3_client.upload_fileobj(fo, BUCKET_NAME, JOB_FILE)

    def user_exist(self, user_name):
        return user_name in self.users
        
    def insert_user(self, user_name):
        self.users.append(user_name)
        self.save_users()

    def delete_user(self, user_name):
        self.users.remove(user_name)
        self.save_users()

    def get_all_users(self):
        return self.users

    def get_all_jobs(self):
        return self.jobs
    
    def get_next_id(self):
        count = 1
        for job in self.jobs:
            if job[0] > count:
                return count
            count += 1
        return count
    
    def insert_job(self, days_str, message, times_str, groups):
        id = self.get_next_id()
        self.jobs.append([id, days_str, message, times_str, True, groups])
        self.save_jobs()

    def delete_job(self, id):
        ID = int(id)
        for index, job in enumerate(self.jobs):
            if job[0] == ID:
                self.jobs.pop(index)
                self.save_jobs()

    def get_job_status(self, id):
        ID = int(id)
        for job in self.jobs:
            if job[0] == ID:
                return job[4]
        return False

    def switch_job(self, new_status, id):
        ID = int(id)
        for job in self.jobs:
            if job[0] == ID:
                job[4] = new_status
                self.save_jobs()