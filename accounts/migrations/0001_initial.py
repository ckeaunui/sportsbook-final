# Generated by Django 4.2.4 on 2023-09-09 09:22

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True)),
                ('match_id', models.CharField(max_length=100, null=True)),
                ('description', models.CharField(max_length=100, null=True)),
                ('price', models.CharField(max_length=50, null=True)),
                ('wager', models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('to_win', models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(10000.0)])),
                ('match_date', models.CharField(max_length=50, null=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Wager Won', 'Wager Won'), ('Wager Lost', 'Wager Lost'), ('Draw', 'Draw'), ('Void', 'Void')], default='Pending', max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, null=True)),
                ('balance', models.FloatField(default=0, null=True)),
                ('pending', models.FloatField(default=0, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('freeplay', models.FloatField(default=0, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('bets', models.ManyToManyField(blank=True, null=True, to='accounts.bet')),
                ('user', models.OneToOneField(default='Guest', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_ordered', models.BooleanField(default=False)),
                ('date_added', models.DateTimeField(auto_now=True)),
                ('date_ordered', models.DateTimeField(null=True)),
                ('product', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.bet')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ref_code', models.CharField(max_length=15)),
                ('is_ordered', models.BooleanField(default=False)),
                ('date_ordered', models.DateTimeField(auto_now=True)),
                ('items', models.ManyToManyField(to='accounts.orderitem')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.customer')),
            ],
        ),
    ]