# Generated by Django 4.2.4 on 2023-09-10 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_customer_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='bets',
            field=models.ManyToManyField(blank=True, to='accounts.bet'),
        ),
    ]