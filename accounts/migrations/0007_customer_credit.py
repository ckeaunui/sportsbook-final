# Generated by Django 4.2.4 on 2023-09-14 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_cart_cartitem_product_remove_order_bets_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='credit',
            field=models.FloatField(default=0.0, null=True),
        ),
    ]
