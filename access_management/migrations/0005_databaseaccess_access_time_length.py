# Generated by Django 5.0.2 on 2024-02-21 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('access_management', '0004_databaseaccess_granted_database_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='databaseaccess',
            name='access_time_length',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
