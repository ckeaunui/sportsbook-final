# Generated by Django 4.2.4 on 2023-09-30 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0022_remove_order_is_ordered_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='point',
            field=models.FloatField(null=True),
        ),
    ]