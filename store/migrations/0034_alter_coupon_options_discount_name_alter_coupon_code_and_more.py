# Generated by Django 5.0.6 on 2024-05-29 06:37

import django.core.validators
import store.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0033_order_applied_coupon_order_grand_total'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='coupon',
            options={'ordering': ['-valid_to']},
        ),
        migrations.AddField(
            model_name='discount',
            name='name',
            field=models.CharField(default='a', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='coupon',
            name='code',
            field=models.CharField(max_length=50, unique=True, validators=[django.core.validators.RegexValidator(message='Please use uppercase letters and numbers only (up to 10 characters).', regex='^[A-Z0-9]{1,10}$')]),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='discount',
            field=models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='valid_from',
            field=models.DateField(validators=[store.models.validate_valid_from]),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='valid_to',
            field=models.DateField(validators=[store.models.validate_valid_to]),
        ),
        migrations.AlterField(
            model_name='discount',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='discount',
            name='discount',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterUniqueTogether(
            name='coupon',
            unique_together={('name', 'discount')},
        ),
    ]
