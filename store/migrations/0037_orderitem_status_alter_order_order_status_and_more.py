# Generated by Django 5.0.6 on 2024-05-30 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0036_customer_wallet_balance_delete_wallet'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='status',
            field=models.CharField(choices=[('P', 'Pending'), ('C', 'Cancelled'), ('RR', 'Return Requested'), ('RA', 'Return Approved'), ('S', 'Shipped'), ('D', 'Delivered')], default='P', max_length=2),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('PL', 'Placed'), ('PR', 'Processing'), ('CO', 'Completed'), ('CA', 'Cancelled')], default='PL', max_length=2),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['order_status'], name='store_order_order_s_4977c5_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['payment_status'], name='store_order_payment_83b142_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['customer'], name='store_order_custome_5796e7_idx'),
        ),
    ]
