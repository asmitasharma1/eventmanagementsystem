# Generated by Django 4.2.5 on 2024-10-27 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0008_event_is_free'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='download_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
