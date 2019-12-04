# Generated by Django 2.0.6 on 2018-08-25 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nrega', '0027_task_inprogress'),
    ]

    operations = [
        migrations.CreateModel(
            name='LanguageDict',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phrase1', models.CharField(max_length=1024)),
                ('lang1', models.CharField(max_length=1024)),
                ('phrase2', models.CharField(blank=True, max_length=1024, null=True)),
                ('lang2', models.CharField(blank=True, max_length=1024, null=True)),
            ],
            options={
                'db_table': 'languageDict',
            },
        ),
    ]