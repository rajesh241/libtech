# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-15 01:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nrega', '0171_auto_20171009_0726'),
    ]

    operations = [
        migrations.CreateModel(
            name='PanchayatCrawlQueue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.PositiveSmallIntegerField(default=0)),
                ('progress', models.PositiveSmallIntegerField(default=0)),
                ('downloadAttemptCount', models.PositiveSmallIntegerField(default=0)),
                ('crawlStartDate', models.DateTimeField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified', models.DateTimeField(auto_now=True, null=True)),
                ('isComplete', models.BooleanField(default=False)),
                ('isError', models.BooleanField(default=False)),
                ('error', models.CharField(blank=True, max_length=1024, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='panchayat',
            name='accuracyIndex',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='panchayat',
            name='accuracyIndexAverage',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='panchayat',
            name='lastCrawlDate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='panchayat',
            name='lastCrawlDuration',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='applicant',
            name='panchayat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Panchayat'),
        ),
        migrations.AlterField(
            model_name='block',
            name='district',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.District'),
        ),
        migrations.AlterField(
            model_name='blockreport',
            name='block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Block'),
        ),
        migrations.AlterField(
            model_name='district',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.State'),
        ),
        migrations.AlterField(
            model_name='fpsshop',
            name='block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Block'),
        ),
        migrations.AlterField(
            model_name='fto',
            name='block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Block'),
        ),
        migrations.AlterField(
            model_name='jobcard',
            name='panchayat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='nrega.Panchayat'),
        ),
        migrations.AlterField(
            model_name='muster',
            name='block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Block'),
        ),
        migrations.AlterField(
            model_name='muster',
            name='panchayat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='nrega.Panchayat'),
        ),
        migrations.AlterField(
            model_name='nicblockreport',
            name='block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Block'),
        ),
        migrations.AlterField(
            model_name='panchayat',
            name='block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Block'),
        ),
        migrations.AlterField(
            model_name='panchayatreport',
            name='panchayat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Panchayat'),
        ),
        migrations.AlterField(
            model_name='panchayatstat',
            name='panchayat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Panchayat'),
        ),
        migrations.AlterField(
            model_name='phonebook',
            name='panchayat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='nrega.Panchayat'),
        ),
        migrations.AlterField(
            model_name='stat',
            name='panchayat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='nrega.Panchayat'),
        ),
        migrations.AlterField(
            model_name='village',
            name='panchayat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='nrega.Panchayat'),
        ),
        migrations.AlterField(
            model_name='wagelist',
            name='block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Block'),
        ),
        migrations.AddField(
            model_name='panchayatcrawlqueue',
            name='panchayat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nrega.Panchayat'),
        ),
    ]
