# Generated by Django 2.0.6 on 2018-08-22 00:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nrega', '0024_task_libname'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='isError',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='task',
            name='libName',
            field=models.CharField(default='crawl', max_length=256),
        ),
    ]
