# Generated by Django 2.0.6 on 2018-08-17 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nrega', '0008_auto_20180815_1125'),
    ]

    operations = [
        migrations.AddField(
            model_name='crawlstate',
            name='isPanchayatLevelProcess',
            field=models.BooleanField(default=False),
        ),
    ]
