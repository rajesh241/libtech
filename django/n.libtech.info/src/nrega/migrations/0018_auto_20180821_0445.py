# Generated by Django 2.0.6 on 2018-08-20 23:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nrega', '0017_auto_20180820_1858'),
    ]

    operations = [
        migrations.AddField(
            model_name='worker',
            name='is15Days',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='worker',
            name='isExtraSample',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='worker',
            name='isExtraSample30',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='worker',
            name='isSample',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='worker',
            name='isSample30',
            field=models.BooleanField(default=False),
        ),
    ]
