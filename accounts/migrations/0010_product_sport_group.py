# Generated by Django 4.2.4 on 2023-09-17 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_rename_match_date_product_commence_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sport_group',
            field=models.CharField(max_length=150, null=True),
        ),
    ]
