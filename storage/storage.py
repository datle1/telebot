from abc import abstractmethod


class Storage():

    @abstractmethod
    def pre_config(self):
        pass

    @abstractmethod
    def user_exist(self, username):
        pass

    @abstractmethod
    def insert_user(self, username):
        pass

    @abstractmethod
    def delete_user(self, username):
        pass

    @abstractmethod
    def get_all_users(self):
        pass

    @abstractmethod
    def get_all_jobs(self):
        pass

    @abstractmethod
    def insert_job(self, days_str, message, times_str, groups):
        pass

    @abstractmethod
    def del_job(self, id):
        pass

    @abstractmethod
    def get_job_status(self, id):
        pass

    @abstractmethod
    def switch_job(self, new_status, id):
        pass