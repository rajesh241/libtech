# Generated by Django 2.0.6 on 2018-08-12 23:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nrega', '0004_crawlstate_iteratefinyear'),
    ]

    operations = [
        migrations.RenameField(
            model_name='crawlstate',
            old_name='iterateFinyear',
            new_name='iterateFinYear',
        ),
    ]
