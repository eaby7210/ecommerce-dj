# Generated by Django 5.0.4 on 2024-04-11 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_rename_promotion_discount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
