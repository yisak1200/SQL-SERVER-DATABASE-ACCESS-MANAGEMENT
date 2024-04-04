# myapp/management/commands/auto_execute.py
from django.core.management.base import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time
from access_management.models import DatabaseAccess
from django.utils import timezone
from django.db import connections
import requests
class Command(BaseCommand):
    help = 'Automatically execute code every 10 seconds'

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.CloseDbAutomatically, 'interval', seconds=10)
        scheduler.start()

        try:
            while True:
                time.sleep(2) 
        except KeyboardInterrupt:
            scheduler.shutdown()

    def execute_code(self):
        print("Executing code at:", datetime.now())
    def CloseDbAutomatically(self):
        granted_dbs = DatabaseAccess.objects.filter(access_status="Granted")
        current_datetime_server_timezone = datetime.now()

        for granted in granted_dbs:
            access_end_time_naive = timezone.localtime(granted.access_end_time, timezone.get_current_timezone()).replace(tzinfo=None)

            if access_end_time_naive <= current_datetime_server_timezone and granted.granted_database2 is None:
                db_username = granted.database_username
                db_password = granted.database_password
                host_address = granted.host_address
            
            # Establish database connection
                try:
                    conn = connections['sql_server1']
                    conn.settings_dict['USER'] = db_username
                    conn.settings_dict['PASSWORD'] = db_password
                    conn.settings_dict['HOST'] = host_address
                    conn.connect()
                    cursor = conn.cursor()
                
                # Revoke database access
                    granted_db_name = granted.granted_database
                    granted_username = granted.access_db_username
                    Revoke_DB_Access = f"""
                    USE [{granted_db_name}];
                    ALTER ROLE db_owner DROP MEMBER [{granted_username}];
                    DROP USER [{granted_username}];
                """
                    cursor.execute(Revoke_DB_Access)

                # Update access status
                    granted.access_status = 'Closed'
                    granted.access_closed_date = current_datetime_server_timezone
                    granted.save()
                    access_given_date = granted.access_given_date.strftime('%b. %d, %Y, %I:%M %p')
                    access_end_time = granted.access_end_time.strftime('%b. %d, %Y, %I:%M %p')
                    ClosedDB = (          
            f"The following Database Access Has been Closed \n"          
            f"Database Granted For: {granted.access_given_to} \n"
            f"Granted Database Name: {granted.granted_database}\n"
            f"UN: {granted.access_db_username}\n"
            f"PD: {granted.database_access_password}\n"
            f"Addresses: {granted.host_address}\n"
            f"Access Given Date: {access_given_date}\n"
            f"Access Expiration Date: {access_end_time}\n" 
            f"Access Given By: {granted.Access_give_by.first_name} {granted.Access_give_by.last_name}"
        )
                    base_url ='https://api.telegram.org/bot6793850859:AAFxLZ5HPEvWXREZSGlRK3mN0uE8VV05fRw/sendMessage?chat_id=-4130253999&text="{}" '.format(ClosedDB)
                    requests.get(base_url)

                    print(ClosedDB)
                except Exception as e:
                    message_error = f"An error occurred: {e}"
                    print('-------------', message_error)     
            elif access_end_time_naive <= current_datetime_server_timezone and granted.granted_database2 is not None:
                db_username = granted.database_username
                db_password = granted.database_password
                host_address = granted.host_address
            
            # Establish database connection
                try:
                    conn = connections['sql_server1']
                    conn.settings_dict['USER'] = db_username
                    conn.settings_dict['PASSWORD'] = db_password
                    conn.settings_dict['HOST'] = host_address
                    conn.connect()
                    cursor = conn.cursor()
                
                # Revoke database access
                    granted_db_name = granted.granted_database
                    granted_db_name2 = granted.granted_database2
                    granted_username = granted.access_db_username
                    Revoke_DB_Access = f"""
                    USE [{granted_db_name}];
                    ALTER ROLE db_owner DROP MEMBER [{granted_username}];
                    DROP USER [{granted_username}];
                    USE [{granted_db_name2}];
                    ALTER ROLE db_owner DROP MEMBER [{granted_username}];
                    DROP USER [{granted_username}];
                """
                    cursor.execute(Revoke_DB_Access)

                # Update access status
                    granted.access_status = 'Closed'
                    granted.access_closed_date = current_datetime_server_timezone
                    granted.save()
                    access_given_date = granted.access_given_date.strftime('%b. %d, %Y, %I:%M %p')
                    access_end_time = granted.access_end_time.strftime('%b. %d, %Y, %I:%M %p')
                    ClosedDB = (           
            f"The Following Databases Access Has been Closed \n"          
            f"Database Granted For: {granted.access_given_to} \n"
            f"Granted Database Name: {granted.granted_database} and {granted.granted_database2}\n"
            f"UN: {granted.access_db_username}\n"
            f"PD: {granted.database_access_password}\n"
            f"Addresses: {granted.host_address}\n"
            f"Access Given Date: {access_given_date}\n"
            f"Access Expiration Date: {access_end_time}\n" 
            f"Access Given By: {granted.Access_give_by.first_name} {granted.Access_give_by.last_name}" 
        )
                    base_url ='https://api.telegram.org/bot6793850859:AAFxLZ5HPEvWXREZSGlRK3mN0uE8VV05fRw/sendMessage?chat_id=-4130253999&text="{}" '.format(ClosedDB)
                    requests.get(base_url)
                    print(ClosedDB)
                except Exception as e:
                    message_error = f"An error occurred: {e}"
                    print('-------------', message_error)                   
    
