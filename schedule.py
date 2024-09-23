import datetime
import sqlite3
import time
import requests
import os
from dotenv import load_dotenv
from storage.storage_factory import StorageFactory

load_dotenv()

TOKEN = os.getenv('TOKEN')
storage = StorageFactory.get_storage('s3')

def schedule():
    while True:
        try:
            current_datetime = datetime.datetime.now()
            sent = False
            
            # Select all columns for jobs
            jobs = storage.get_all_jobs()
            for job in jobs:
                status = job[4]
                if status == True:
                    # Get all from job
                    day_number = job[1].split(',')
                    task = job[2]
                    time_in_day = job[3].split(',')
                    group_list = job[5].split(',')
                    
                    # Get current day number (1-31)
                    current_day_number = current_datetime.day
                    current_day_of_week = current_datetime.weekday()
                    current_time_formatted = current_datetime.strftime("%H:%M")
                
                    # Get current day of the week (Monday = 0, Sunday = 6)
                    days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                    current_day_name = days_of_week[current_day_of_week]
                    
                    if current_time_formatted in time_in_day:
                        if (str(current_day_number) in day_number and current_day_name != "saturday" and current_day_name != "sunday") or (current_day_name in day_number):
                            for group_id in group_list:
                                url = (f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={group_id}&text={task}")
                                requests.get(url).json
                                sent = True
            if sent:
                time.sleep(60)
            else:
                time.sleep(50)  

        except Exception as e:
            print(f"Error in scheduler: {e}")

if __name__ == "__main__":
    schedule()
