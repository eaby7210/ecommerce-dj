# Generated by Django 5.0.4 on 2024-05-06 09:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_emailaddress_idx_upper_email'),
        ('core', '0004_remove_user_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailOTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('otp', models.CharField(max_length=6)),
                ('email', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='account.emailaddress')),
            ],
        ),
    ]