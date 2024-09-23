import io
from storage.storage import Storage
import boto3
from io import BytesIO
import os

BUCKET_NAME = 'telebucket'
USER_FILE = 'users.txt'
JOB_FILE = 'jobs.txt'
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
        self.users = self.get_all_users()
        self.jobs = self.get_all_jobs()

    def save_users(self):
        fo = io.BytesIO(b"\n".join([bytes(item, 'utf-8') for item in self.users]))
        self.s3_client.upload_fileobj(fo, BUCKET_NAME, USER_FILE)

    def save_jobs(self):
        fo = io.BytesIO(b"\n".join([bytes(item, 'utf-8') for item in self.jobs]))
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
        f = BytesIO()
        self.s3_client.download_fileobj(BUCKET_NAME, USER_FILE, f)
        users = f.getvalue().decode("utf-8").split('\n')
        return users

    def get_all_jobs(self):
        f = BytesIO()
        self.s3_client.download_fileobj(BUCKET_NAME, JOB_FILE, f)
        jobs = f.getvalue().decode("utf-8").split('\n')
        return jobs
    
    def insert_job(self, days_str, message, times_str, groups):
        self.jobs.append("|".join(days_str, message, times_str, True, groups))
        self.save_jobs()

    def delete_job(self, id):
        self.jobs.pop(id)
        self.save_jobs()

    def get_job_status(self, id):
        job = self.jobs.__getitem__(id).split("|")
        return bool(job[3])

    def switch_job(self, new_status, id):
        job = self.jobs.__getitem__(id).split("|")
        job[3] = new_status
        self.jobs.__setitem__(id, "|".join(job))
        self.save_jobs()