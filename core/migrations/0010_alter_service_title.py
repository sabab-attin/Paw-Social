# Generated by Django 4.2.9 on 2025-01-04 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_shop_product_name_alter_shop_quantity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
