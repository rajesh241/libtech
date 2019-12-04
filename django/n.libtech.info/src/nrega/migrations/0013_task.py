# Generated by Django 2.0.6 on 2018-08-19 08:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nrega', '0012_crawlstate_objlimit'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('processName', models.CharField(blank=True, max_length=256, null=True)),
                ('objID', models.IntegerField(blank=True, null=True)),
                ('hasDownloadManager', models.BooleanField(default=False)),
                ('finyear', models.CharField(max_length=2)),
                ('isComplete', models.BooleanField(default=False)),
                ('crawlQueue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.CrawlQueue')),
            ],
            options={
                'db_table': 'task',
            },
        ),
    ]