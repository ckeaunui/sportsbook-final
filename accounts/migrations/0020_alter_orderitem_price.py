# Generated by Django 4.2.4 on 2023-09-29 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0019_remove_orderitem_description_remove_orderitem_game_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='price',
            field=models.IntegerField(null=True),
        ),
    ]
