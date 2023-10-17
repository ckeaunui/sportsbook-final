# Generated by Django 4.2.4 on 2023-10-04 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0025_order_is_ordered'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('Credit', 'Credit'), ('Freeplay', 'Freeplay')], default='Credit', max_length=100),
        ),
    ]