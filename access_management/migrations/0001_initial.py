# Generated by Django 5.0.2 on 2024-02-15 12:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DatabaseAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_detail', models.TextField()),
                ('access_given_date', models.DateTimeField(auto_now_add=True)),
                ('host_address', models.CharField(blank=True, max_length=200, null=True)),
                ('database_username', models.CharField(blank=True, max_length=200, null=True)),
                ('database_password', models.CharField(blank=True, max_length=200, null=True)),
                ('access_start_time', models.DateTimeField()),
                ('access_end_time', models.DateTimeField()),
                ('access_status', models.CharField(choices=[('Granted', 'Granted'), ('Closed', 'Closed')], max_length=20)),
                ('Access_give_by', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]