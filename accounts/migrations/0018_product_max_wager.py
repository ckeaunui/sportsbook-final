# Generated by Django 4.2.4 on 2023-09-28 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_alter_product_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='max_wager',
            field=models.FloatField(null=True),
        ),
    ]