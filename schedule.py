import datetime
import sqlite3
import time
import requests
import os
import dotenv from load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

conn = sqlite3.connect('mydatabase.db')
cursor = conn.cursor()

def scheduler():
    while True:
        try:
            # Select all columns for jobs where status is True
            cursor.execute('SELECT * FROM job WHERE status = ?', (True,))
            jobs = cursor.fetchall()

            for job in jobs:
                current_datetime = datetime.datetime.now()

                # Get current day number (1-31)
                current_day_number = current_datetime.day
                current_day_of_week = current_datetime.weekday()
                current_time_formatted = current_datetime.strftime("%H:%M")
               
                # Get current day of the week (Monday = 0, Sunday = 6)
                days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                current_day_name = days_of_week[current_day_of_week]
                
                if (str(current_day_number) in job[1]) or (current_day_name in job[1]):
                    if current_time_formatted in job[3]:
                        url = (f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={job[2]}")
                        requests.get(url).json
                    #else:
                        #print("Unavailable")
                #else:
                    #print("Unavailable")

            time.sleep(30)  

        except Exception as e:
            print(f"Error in scheduler: {e}")


def main():
    scheduler()

main()
