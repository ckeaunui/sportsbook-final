# Generated by Django 4.2.4 on 2023-10-11 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0032_remove_cart_products_cartitem_cart'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='name',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
