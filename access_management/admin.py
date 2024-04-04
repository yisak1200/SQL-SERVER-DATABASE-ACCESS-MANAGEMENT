from django.contrib import admin
from .models import DatabaseAccess

class DatabaseAccessAdmin(admin.ModelAdmin):
    list_display = ('host_address', 'granted_database','granted_database2','database_access_password', 'access_db_username', 'access_status', 'access_given_date','access_end_time','access_time_length')
    list_filter = ('access_status', 'access_given_date')
    search_fields = ('host_address', 'granted_database', 'access_db_username', 'access_detail')
    readonly_fields = ('access_given_date',)

admin.site.register(DatabaseAccess, DatabaseAccessAdmin)
