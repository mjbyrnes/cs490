# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-02 06:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FormD',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cik', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=500)),
                ('year_of_incorp', models.CharField(max_length=30)),
                ('street1', models.CharField(max_length=100)),
                ('street2', models.CharField(max_length=100)),
                ('zip_code', models.CharField(max_length=10)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=10)),
                ('ind_group_type', models.CharField(max_length=100)),
                ('min_investment_accepted', models.IntegerField()),
                ('total_amount_sold', models.IntegerField()),
                ('total_offering_amount', models.IntegerField()),
                ('total_remaining', models.IntegerField()),
                ('has_non_accred', models.BooleanField()),
                ('num_non_accred', models.IntegerField()),
                ('tot_number_investors', models.IntegerField()),
            ],
        ),
    ]
