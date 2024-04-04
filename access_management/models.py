from django.db import models
from django.contrib.auth.models import User
class DatabaseAccess(models.Model):
    ACCESS_STATUS_CHOICES = (
        ('Granted', 'Granted'),
        ('Closed', 'Closed'),   
    )
    Access_give_by = models.ForeignKey(User, on_delete=models.CASCADE)
    access_detail  = models.TextField()
    host_address = models.CharField(max_length=200,null=True,blank=True)
    database_username =models.CharField(max_length=200,null=True,blank=True)
    database_password = models.CharField(max_length=200,null=True,blank=True)
    access_given_date = models.DateTimeField(null=True,blank=True)
    granted_database = models.CharField(max_length=100,null=True,blank=True)
    granted_database2 = models.CharField(max_length=200,null=True,blank=True)
    access_time_length = models.CharField(max_length=100,null=True,blank=True)
    access_end_time = models.DateTimeField()
    access_db_username = models.CharField(max_length=50,null=True,blank=True)
    database_access_password = models.CharField(max_length=100,null=True,blank=True)
    access_given_to = models.CharField(max_length=100,null=True,blank=True)
    access_closed_date = models.DateTimeField(null=True,blank=True)
    access_status = models.CharField(
        max_length=20, choices=ACCESS_STATUS_CHOICES,default='Granted')
    
    

