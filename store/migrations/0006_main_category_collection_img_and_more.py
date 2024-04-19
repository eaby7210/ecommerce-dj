# Generated by Django 5.0.4 on 2024-04-18 06:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_remove_customer_wallet_wallet'),
    ]

    operations = [
        migrations.CreateModel(
            name='Main_Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('descriptions', models.TextField(default='Default Description')),
                ('img', models.ImageField(blank=True, default='null', null=True, upload_to='store/categories')),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.AddField(
            model_name='collection',
            name='img',
            field=models.ImageField(blank=True, default='null', null=True, upload_to='store/collections'),
        ),
        migrations.AlterField(
            model_name='product',
            name='collection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='collection_products', to='store.collection'),
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cotegory_products', to='store.main_category'),
        ),
    ]
