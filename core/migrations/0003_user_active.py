# Generated by Django 5.0.4 on 2024-04-10 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_user_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]
