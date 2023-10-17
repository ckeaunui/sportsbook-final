# Generated by Django 4.2.4 on 2023-09-29 01:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_product_max_wager'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='description',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='game',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.product'),
        ),
    ]