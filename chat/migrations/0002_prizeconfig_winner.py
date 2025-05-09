# Generated by Django 5.2 on 2025-04-28 16:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
        ('users', '0002_userprofile_access_expiry_time_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrizeConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prize_name', models.CharField(max_length=255)),
                ('prize_amount', models.DecimalField(decimal_places=8, max_digits=18)),
                ('trigger_phrases', models.JSONField(help_text='List of specific phrases that trigger a win')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Winner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('won_at', models.DateTimeField(auto_now_add=True)),
                ('prize', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.prizeconfig')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.userprofile')),
            ],
        ),
    ]
