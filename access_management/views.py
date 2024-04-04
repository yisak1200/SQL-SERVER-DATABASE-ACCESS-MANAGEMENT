from django.shortcuts import render, redirect
from django.views import View
from datetime import datetime, timedelta
from django.db import connections, OperationalError
from .models import DatabaseAccess
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.utils import OperationalError
import random
import string
def generate_random_password(length=20):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))

    return password

class IndexPage(LoginRequiredMixin,View):
    def get(self, request):
        return render(request, 'base_temp/index.html')
class ConnectToDatabase(LoginRequiredMixin,View):
    def get(self, request):
        return render(request, 'base_temp/connect_to_DB.html')
    def post(self, request):
        action = request.POST.get('action')
        if action == 'test_connection':
            host_address = request.POST.get('host-address')
            db_username = request.POST.get('Db-username')
            db_password = request.POST.get('Db-password')
            current_datetime = datetime.now()
            if not all([host_address, db_username, db_password]):
                message_error = "Incomplete database information. Please provide all required fields."
                return render(request, 'base_temp/connect_to_DB.html', {'message_error': message_error})

            conn = connections['sql_server']
            conn.settings_dict['USER'] = db_username
            conn.settings_dict['PASSWORD'] = db_password
            conn.settings_dict['HOST'] = host_address

            if not conn.settings_dict['USER'] or not conn.settings_dict['PASSWORD'] or not conn.settings_dict['HOST']:
                message_error = "Incomplete database information. Please provide all required fields."
                return render(request, 'base_temp/connect_to_DB.html', {'message_error': message_error})

            if conn.settings_dict['HOST'] == 'invalid_host':
                message_error = "Invalid host address."
                return render(request, 'base_temp/connect_to_DB.html', {'message_error': message_error})

            if conn.settings_dict['USER'] == 'invalid_user':
                message_error = "Invalid database username."
                return render(request, 'base_temp/connect_to_DB.html', {'message_error': message_error})

            if conn.settings_dict['PASSWORD'] == 'invalid_password':
                message_error = "Invalid database password."
                return render(request, 'base_temp/connect_to_DB.html', {'message_error': message_error})

            try:
            # Connect to the database
                conn.connect()

            # Fetch list of databases
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sys.databases WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb') ORDER BY name ASC")
                databases = [row[0] for row in cursor.fetchall()]
                cursor.execute("""
                    SELECT name
FROM sys.server_principals
WHERE type = 'S'  -- Filter only SQL Server authentication users
AND is_disabled = 0  -- Check for active login users
AND name NOT IN (
    SELECT DISTINCT dp.name
    FROM sys.server_principals sp
    JOIN sys.database_principals dp ON sp.sid = dp.sid
)
AND name NOT IN (
    SELECT DISTINCT sp.name
    FROM sys.server_principals sp
    JOIN sys.server_role_members srm ON sp.principal_id = srm.member_principal_id
    JOIN sys.database_principals dp ON srm.role_principal_id = dp.principal_id
)
ORDER BY name;


            """)
                login_users = [row[0] for row in cursor.fetchall()]

                
                cursor.close()
            # Close the connection
                conn.close()

            # Connection established successfully, add success message and database list to context
                message_succ = "Database connection established successfully!"
                context = {
                'message_succ': message_succ,
                'host_address': host_address,
                'db_username': db_username,
                'db_password': db_password,
                'databases': databases,
                'login_users':login_users
                }
                return render(request, 'base_temp/connect_to_DB.html', context)
            except Exception as e:
            # If connection is not established correctly, generate an error message
                message_error = f"Failed to establish a connection to the database: {e}"
            return render(request, 'base_temp/connect_to_DB.html', {'message_error': message_error})
        elif action == 'give_access':
            host_address = request.POST.get('host-address')
            db_username = request.POST.get('Db-username')
            db_password = request.POST.get('Db-password')
            db_name = request.POST.get('database')
            db_login_name = request.POST.get('db-login')
            db_login_password = request.POST.get('Db-access-password')
            access_detail = request.POST.get('DB-access-letter')
            access_given_to = request.POST.get('access-given-to')
            duration_time = int(request.POST.get('Duration-time'))
            time_measurment = request.POST.get('time-measurment')
            access_time_length = str(duration_time) + " " + str(time_measurment)
            conn = connections['sql_server']
            conn.settings_dict['USER'] = db_username
            conn.settings_dict['PASSWORD'] = db_password
            conn.settings_dict['HOST'] = host_address
            db_access_filter = DatabaseAccess.objects.filter(host_address=host_address,access_db_username=db_login_name,access_status='Granted').count()
            if db_access_filter == 1:
                message_error = "This username is already granted for Other Database in this host :" + host_address
                context = {'message_error':message_error,
                'host_address': host_address,
                'db_username':db_username,
                'db_password':db_password,
                'db_name':db_name,
                'db_login_name':db_login_name,
                'access_time_length':access_time_length,
                'time_measurment':time_measurment,
                'access_detail':access_detail
                }
                return render(request,'base_temp/connect_to_DB.html',context)
            else:
                try:
        # Connect to the database
                    conn.connect()
                    cursor = conn.cursor()

        # Construct and execute the SQL queries
                    password = generate_random_password()
                    change_password_query = f"ALTER LOGIN [{db_login_name}] WITH PASSWORD = '{password}' , DEFAULT_DATABASE=[{db_name}];"
                    cursor.execute(change_password_query)

                    grant_access_query = f"USE [{db_name}]; CREATE USER [{db_login_name}] FOR LOGIN [{db_login_name}]; ALTER ROLE db_owner ADD MEMBER [{db_login_name}];"
                    cursor.execute(grant_access_query)
                    cursor.close()
                    conn.close()
                    current_datetime_utc = timezone.now()
                    current_datetime_server_timezone = datetime.now()
                    if time_measurment == 'minute':
                        access_end_time = current_datetime_server_timezone + timedelta(minutes=duration_time)
                    elif time_measurment == 'hour':
                        access_end_time = current_datetime_server_timezone + timedelta(hours=duration_time)  
                    elif time_measurment == 'day':
                        access_end_time = current_datetime_server_timezone + timedelta(days=duration_time) 
                    elif time_measurment =='week':
                        access_end_time = current_datetime_server_timezone + timedelta(weeks=duration_time)        
                    database_access = DatabaseAccess(Access_give_by = request.user,access_detail=access_detail,host_address=host_address,database_username=db_username,database_password=db_password,database_access_password=password,access_end_time=access_end_time,granted_database=db_name,access_time_length=access_time_length,access_db_username=db_login_name,access_given_date=current_datetime_server_timezone,access_given_to=access_given_to)
                    database_access.save()
                    message_succ = "DB access granted successfully!"
                    context = {'message_succ':message_succ}
                    return render(request,'base_temp/connect_to_DB.html',context)
                except Exception as e:
                    message_error = f"Failed to grant DB access: {e}"
                return render(request, 'base_temp/connect_to_DB.html', {'message_error': message_error})
class GiveTwoDBAccess(View):
    def get(self,request):
        return render(request,'base_temp/Give_two_DB_access.html')  
    def post(self,request):
        action = request.POST.get('action')
        if action == 'test_connection':
            host_address = request.POST.get('host-address')
            db_username = request.POST.get('Db-username')
            db_password = request.POST.get('Db-password')
            current_datetime = datetime.now()
            if not all([host_address, db_username, db_password]):
                message_error = "Incomplete database information. Please provide all required fields."
                return render(request, 'base_temp/Give_two_DB_access.html', {'message_error': message_error})

            conn = connections['sql_server']
            conn.settings_dict['USER'] = db_username
            conn.settings_dict['PASSWORD'] = db_password
            conn.settings_dict['HOST'] = host_address

            if not conn.settings_dict['USER'] or not conn.settings_dict['PASSWORD'] or not conn.settings_dict['HOST']:
                message_error = "Incomplete database information. Please provide all required fields."
                return render(request, 'base_temp/Give_two_DB_access.html', {'message_error': message_error})

            if conn.settings_dict['HOST'] == 'invalid_host':
                message_error = "Invalid host address."
                return render(request, 'base_temp/Give_two_DB_access.html', {'message_error': message_error})

            if conn.settings_dict['USER'] == 'invalid_user':
                message_error = "Invalid database username."
                return render(request, 'base_temp/Give_two_DB_access.html', {'message_error': message_error})

            if conn.settings_dict['PASSWORD'] == 'invalid_password':
                message_error = "Invalid database password."
                return render(request, 'base_temp/Give_two_DB_access.html', {'message_error': message_error})

            try:
            # Connect to the database
                conn.connect()

            # Fetch list of databases
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sys.databases WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb') ORDER BY name ASC")
                databases = [row[0] for row in cursor.fetchall()]
                cursor.execute("""
                    SELECT name
FROM sys.server_principals
WHERE type = 'S'  -- Filter only SQL Server authentication users
AND is_disabled = 0  -- Check for active login users
AND name NOT IN (
    SELECT DISTINCT dp.name
    FROM sys.server_principals sp
    JOIN sys.database_principals dp ON sp.sid = dp.sid
)
AND name NOT IN (
    SELECT DISTINCT sp.name
    FROM sys.server_principals sp
    JOIN sys.server_role_members srm ON sp.principal_id = srm.member_principal_id
    JOIN sys.database_principals dp ON srm.role_principal_id = dp.principal_id
)
ORDER BY name;


            """)
                login_users = [row[0] for row in cursor.fetchall()]

                
                cursor.close()
            # Close the connection
                conn.close()

            # Connection established successfully, add success message and database list to context
                message_succ = "Database connection established successfully!"
                context = {
                'message_succ': message_succ,
                'host_address': host_address,
                'db_username': db_username,
                'db_password': db_password,
                'databases': databases,
                'login_users':login_users
                }
                return render(request, 'base_temp/Give_two_DB_access.html', context)
            except Exception as e:
            # If connection is not established correctly, generate an error message
                message_error = f"Failed to establish a connection to the database: {e}"
            return render(request, 'base_temp/Give_two_DB_access.html', {'message_error': message_error})
        elif action == 'give_access':
            host_address = request.POST.get('host-address')
            db_username = request.POST.get('Db-username')
            db_password = request.POST.get('Db-password')
            db_name = request.POST.get('database')
            db_name2 = request.POST.get('database2')
            db_login_name = request.POST.get('db-login')
            db_login_password = request.POST.get('Db-access-password')
            access_detail = request.POST.get('DB-access-letter')
            access_given_to = request.POST.get('access-given-to')
            duration_time = int(request.POST.get('Duration-time'))
            time_measurment = request.POST.get('time-measurment')
            access_time_length = str(duration_time) + " " + str(time_measurment)
            conn = connections['sql_server']
            conn.settings_dict['USER'] = db_username
            conn.settings_dict['PASSWORD'] = db_password
            conn.settings_dict['HOST'] = host_address
            db_access_filter = DatabaseAccess.objects.filter(host_address=host_address,access_db_username=db_login_name,access_status='Granted').count()
            if db_access_filter == 1:
                message_error = "This username is already granted for Other Database in this host :" + host_address
                context = {'message_error':message_error,
                'host_address': host_address,
                'db_username':db_username,
                'db_password':db_password,
                'db_name':db_name,
                'db_name2':db_name2,
                'db_login_name':db_login_name,
                'access_time_length':access_time_length,
                'time_measurment':time_measurment,
                'access_detail':access_detail
                }
                return render(request,'base_temp/Give_two_DB_access.html',context)
            else:
                try:
                    conn.connect()
                    cursor = conn.cursor()
                    password = generate_random_password()
                    change_password_query = f"ALTER LOGIN [{db_login_name}] WITH PASSWORD = '{password}' , DEFAULT_DATABASE= master;"
                    cursor.execute(change_password_query)
                    grant_access_query = f"""USE [{db_name}]; CREATE USER [{db_login_name}] FOR LOGIN [{db_login_name}]; ALTER ROLE db_owner ADD MEMBER [{db_login_name}];
                    USE [{db_name2}]; CREATE USER [{db_login_name}] FOR LOGIN [{db_login_name}]; ALTER ROLE db_owner ADD MEMBER [{db_login_name}];
                    """
                    cursor.execute(grant_access_query)
                    cursor.close()
                    conn.close()
                    current_datetime_utc = timezone.now()
                    current_datetime_server_timezone = datetime.now()
                    if time_measurment == 'minute':
                        access_end_time = current_datetime_server_timezone + timedelta(minutes=duration_time)
                    elif time_measurment == 'hour':
                        access_end_time = current_datetime_server_timezone + timedelta(hours=duration_time)  
                    elif time_measurment == 'day':
                        access_end_time = current_datetime_server_timezone + timedelta(days=duration_time) 
                    elif time_measurment =='week':
                        access_end_time = current_datetime_server_timezone + timedelta(weeks=duration_time)        
                    database_access = DatabaseAccess(Access_give_by = request.user,access_detail=access_detail,host_address=host_address,database_username=db_username,database_password=db_password,database_access_password=password,access_end_time=access_end_time,granted_database=db_name,access_time_length=access_time_length,access_db_username=db_login_name,access_given_date=current_datetime_server_timezone,access_given_to=access_given_to,granted_database2=db_name2)
                    database_access.save()
                    message_succ = "DB access granted successfully!"
                    context = {'message_succ':message_succ}
                    return render(request,'base_temp/Give_two_DB_access.html',context)
                except Exception as e:
                    message_error = f"Failed to grant DB access: {e}"
                return render(request, 'base_temp/Give_two_DB_access.html', {'message_error': message_error})       
class GivenAccess(LoginRequiredMixin,View):
    def get(self,request):
        database_access = DatabaseAccess.objects.filter(Access_give_by=request.user,access_status="Granted").order_by('-access_given_date')
        context = {'database_access':database_access}
        return render(request,'base_temp/access_given_db.html',context) 
class ClosedAccess(LoginRequiredMixin,View):
    def get(self,request):
        database_access = DatabaseAccess.objects.filter(Access_give_by=request.user,access_status="Closed")
        context = {'database_access':database_access}
        return render(request,'base_temp/closed_access.html',context)           
class ConfirmationLetter(LoginRequiredMixin,View):
    def get(self,request,pk):
        database_access = DatabaseAccess.objects.get(id=pk)
        access_given_date = database_access.access_given_date.strftime('%b. %d, %Y, %I:%M %p')
        access_end_time = database_access.access_end_time.strftime('%b. %d, %Y, %I:%M %p')
        if database_access.granted_database2 is None:
            ConfirmationLetter = (
            f"MS/Mr. {database_access.access_given_to} has been Granted the following database for: {database_access.access_time_length}\n"
            f"{database_access.granted_database}\n"
            f"UN: {database_access.access_db_username}\n"
            f"PD: {database_access.database_access_password}\n"
            f"Addresses: {database_access.host_address}\n"
            f"Access Given Date: {access_given_date}\n"
            f"Access Expiration Date: {access_end_time}\n"   
            )
        else:
            ConfirmationLetter = (
            f"MS/Mr. {database_access.access_given_to} has been Granted the following databases for: {database_access.access_time_length}\n"
            f"{database_access.granted_database} and {database_access.granted_database2}\n"
            f"UN: {database_access.access_db_username}\n"
            f"PD: {database_access.database_access_password}\n"
            f"Addresses: {database_access.host_address}\n"
            f"Access Given Date: {access_given_date}\n"
            f"Access Expiration Date: {access_end_time}\n"   
            )       
        context = {'ConfirmationLetter':ConfirmationLetter}
        return render(request,'base_temp/confirmation_letter.html',context)
    
class CloseAccessManually(View):
    def get(self,request):
        database_access = DatabaseAccess.objects.filter(Access_give_by=request.user,access_status='Granted').order_by('-access_given_date')
        context = {'database_access': database_access}
        return render(request, 'base_temp/access_given_db.html', context)
    def post(self, request):
        try:
            granted_db_id = request.POST.get('granted_db_id')
            if granted_db_id is not None:
                pk = int(granted_db_id)
                granted_access = DatabaseAccess.objects.get(id=pk)
                host_address = granted_access.host_address
                db_username = granted_access.database_username
                db_password = granted_access.database_password
                granted_db_name = granted_access.granted_database
                granted_db_name2 = granted_access.granted_database2
                granted_username = granted_access.access_db_username
                
                if granted_access.access_status == 'Granted' and granted_access.granted_database2 is not None:
                    conn = connections['sql_server1']
                    conn.settings_dict['USER'] = db_username
                    conn.settings_dict['PASSWORD'] = db_password
                    conn.settings_dict['HOST'] = host_address
                    conn.connect()
                    cursor = conn.cursor()
                    Revoke_DB_Access = f"""
                            USE [{granted_db_name}];
                            ALTER ROLE db_owner DROP MEMBER [{granted_username}]
                            DROP USER [{granted_username}];
                            USE [{granted_db_name2}];
                            ALTER ROLE db_owner DROP MEMBER [{granted_username}]
                            DROP USER [{granted_username}];
                            """
                    cursor.execute(Revoke_DB_Access)

                    # Update access status
                    current_datetime_utc = timezone.now()
                    current_datetime_server_timezone = datetime.now()
                    granted_access.access_status = 'Closed'
                    granted_access.access_closed_date = current_datetime_server_timezone
                    granted_access.save()
                    
                    message_succ = "Access Closed Successfully"
                    database_access = DatabaseAccess.objects.filter(Access_give_by=request.user).order_by('-access_closed_date')
                    context = {'message_succ': message_succ, 'database_access': database_access}
                    return render(request, 'base_temp/access_given_db.html', context)
                elif granted_access.access_status == 'Granted' and granted_access.granted_database2 is None:
                    conn = connections['sql_server1']
                    conn.settings_dict['USER'] = db_username
                    conn.settings_dict['PASSWORD'] = db_password
                    conn.settings_dict['HOST'] = host_address
                    
                    conn.connect()
                    cursor = conn.cursor()
                    Revoke_DB_Access = f"""
                            USE [{granted_db_name}];
                            ALTER ROLE db_owner DROP MEMBER [{granted_username}]
                            DROP USER [{granted_username}];
                            """
                    cursor.execute(Revoke_DB_Access)

                    # Update access status
                    current_datetime_utc = timezone.now()
                    current_datetime_server_timezone = datetime.now()
                    granted_access.access_status = 'Closed'
                    granted_access.access_closed_date = current_datetime_server_timezone
                    granted_access.save()
                    
                    message_succ = "Access Closed Successfully"
                    database_access = DatabaseAccess.objects.filter(Access_give_by=request.user).order_by('-access_closed_date')
                    context = {'message_succ': message_succ, 'database_access': database_access}
                    return render(request, 'base_temp/access_given_db.html', context)
                else:
                    message_error = f"This Database is Already closed for this user: {granted_username}"
                    context = {"message_error":message_error}
                    return render(request,'base_temp/closed_access.html',context)
                    
            else:
                message_error = "Invalid request. Missing granted_db_id parameter."
                
            database_access = DatabaseAccess.objects.filter(Access_give_by=request.user).order_by('-access_given_date')
            context = {'message_error': message_error, 'database_access': database_access}
            return render(request, 'base_temp/access_given_db.html', context)
        
        except DatabaseAccess.DoesNotExist:
            message_error = "Database Access not found."
        
        except OperationalError as e:
            message_error = f"Failed to connect to the database: {e}"
        
        except Exception as e:
            message_error = f"An error occurred: {e}"
        
        database_access = DatabaseAccess.objects.filter(Access_give_by=request.user).order_by('-access_given_date')
        context = {'message_error': message_error, 'database_access': database_access}
        return render(request, 'base_temp/access_given_db.html', context)