# Generated by Django 2.0.6 on 2018-08-20 01:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nrega', '0015_crawlqueue_isprocessdriven'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
