# Generated by Django 2.0.6 on 2018-08-22 00:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nrega', '0023_libtechprocess'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='libName',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
