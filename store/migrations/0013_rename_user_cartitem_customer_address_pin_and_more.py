# Generated by Django 5.0.4 on 2024-05-02 06:11

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_rename_collection_product_brand'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cartitem',
            old_name='user',
            new_name='customer',
        ),
        migrations.AddField(
            model_name='address',
            name='pin',
            field=models.CharField(default=0, max_length=10, validators=[django.core.validators.RegexValidator(message='Pin number should be 6 digit number.', regex='^\\d{6}$')]),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='cartitem',
            unique_together={('product', 'customer')},
        ),
    ]