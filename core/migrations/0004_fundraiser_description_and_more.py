# Generated by Django 4.2.9 on 2025-01-03 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_fundraiser_donation_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundraiser',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='fundraiser',
            name='donation_history',
            field=models.TextField(blank=True, default='{}'),
        ),
    ]
