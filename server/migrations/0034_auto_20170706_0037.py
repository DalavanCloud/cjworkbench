# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-06 00:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0033_auto_20170630_0017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delta',
            name='workflow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deltas', to='server.Workflow'),
        ),
    ]
