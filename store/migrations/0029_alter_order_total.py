# Generated by Django 5.0.6 on 2024-05-18 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0028_alter_order_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
