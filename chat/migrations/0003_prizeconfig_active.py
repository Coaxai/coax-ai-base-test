# Generated by Django 5.2 on 2025-04-28 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_prizeconfig_winner'),
    ]

    operations = [
        migrations.AddField(
            model_name='prizeconfig',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
