# Generated by Django 5.0.4 on 2024-05-07 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0014_alter_cartitem_quantity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='street',
            new_name='state',
        ),
        migrations.AddField(
            model_name='address',
            name='name',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='address',
            name='other_details',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='address',
            name='primary',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterUniqueTogether(
            name='address',
            unique_together={('primary', 'customer')},
        ),
    ]
