# Generated by Django 4.2.5 on 2024-10-25 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0004_event_ticket_template'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='ticket_template',
            field=models.ImageField(blank=True, null=True, upload_to='myProject/pic/pic/'),
        ),
    ]
