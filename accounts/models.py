from django.db import models
from django.db.models.signals import post_save
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.contrib.auth import get_user_model
import uuid

from .models import *


# Create your models here.
from django.db import models
from django.db.models.signals import post_save
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User 
from .models import *


# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=2000, null=True)

    def __str__(self):
	    return self.name or None


class Match(models.Model):
    match_id = models.CharField(max_length=1500, null=True)
    league  = models.CharField(max_length=1500, null=True)
    sport_title  = models.CharField(max_length=1500, null=True)
    match_name = models.CharField(max_length=2000, null=True)
    team1 = models.CharField(max_length=2000, null=True)
    team2 = models.CharField(max_length=2000, null=True)
    commence_time = models.CharField(max_length=5000, null=True)
    commence_time_unix = models.IntegerField(null=True)

    def __str__(self):
	    return self.match_name or 'name'


class Product(models.Model):
    match = models.ForeignKey(Match, null=True, related_name="children", on_delete=models.CASCADE)
    key = models.CharField(max_length=5000, null=True)
    winner = models.CharField(max_length=2000, null=True)
    description = models.CharField(max_length=1000, null=True)  
    display_data = models.CharField(max_length=1000, null=True)  
    price = models.IntegerField(null=True)
    point = models.FloatField(null=True)
    max_wager = models.FloatField(null=True)
    
    def __str__(self):
	    return (self.key + " " + self.winner) or None


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=2000, null=True)
    credit = models.FloatField(default=0.0, null=True)
    balance = models.FloatField(default=0.0, null=True)
    pending = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)], null=True)
    freeplay = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)], null=True)
    weekly_profit = models.FloatField(default=0.0, null=True)
    total_profit = models.FloatField(default=0.0, null=True)


    def __str__(self):
	    return self.name or None


class OrderItem(models.Model):
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    price = models.IntegerField(null=True)
    max_wager = models.FloatField(null=True)

    def __str__(self):
        return self.product.match.match_name + ': ' + self.product.winner or None


class Order(models.Model):
    STATUSES = (
        ('Pending', 'Pending'),
        ('Wager Won', 'Wager Won'),
        ('Wager Lost', 'Wager Lost'),
        ('Draw', 'Draw'),
        ('Void', 'Void'),
    )

    PAYMENT_METHODS = (
        ('Credit', 'Credit'),
        ('Freeplay', 'Freeplay'),
    )
    
    customer = models.ForeignKey(Customer, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=2000, null=True)
    description = models.CharField(max_length=2000, null=True)
    price = models.IntegerField(null=True)
    wager = models.FloatField(validators=[MinValueValidator(0.0)], null=True)
    to_win = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5_000.0)], null=True)
    status = models.CharField(max_length=500, default='Pending', null=True, choices=STATUSES)
    products = models.ManyToManyField(OrderItem, blank=True, related_name='products')
    date_ordered = models.DateTimeField(auto_now=True)
    payout_date_utx = models.IntegerField(null=True)
    payout_date = models.CharField(max_length=2000, null=True)

    payment_method = models.CharField(max_length=1000, default='Credit', choices=PAYMENT_METHODS)

    def __str__(self):
        return self.customer.name or None
    

class Cart(models.Model):
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.customer.name


class CartItem(models.Model):
    WAGER_TYPES = (
        ('Straight', 'Straight'),
        ('Parlay', 'Parlay'),
    )

    cart = models.ForeignKey(Cart, null=True, on_delete=models.SET_NULL)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    wager = models.FloatField(validators=[MinValueValidator(0.0)], null=True)
    wager_type = models.CharField(max_length=1000, null=True, default='Straight', choices=WAGER_TYPES)

    def __str__(self):
        return self.product.winner or None

class CasinoWager(models.Model):
    GAMES = (
        ('Blackjack', 'Blackjack'),
        ('Roulette', 'Roulette'),
    )

    RESULTS = (
        ('Won', 'Won'),
        ('Lost', 'Lost'),
        ('Draw', 'Draw'),
    )

    customer = models.ForeignKey(Customer, null=True, on_delete=models.CASCADE)
    wager = models.FloatField(validators=[MinValueValidator(0.0)], null=True)
    payout = models.FloatField(validators=[MinValueValidator(0.0)], null=True)
    game = models.CharField(max_length=1000, null=True, choices=GAMES)
    result = models.CharField(max_length=1000, null=True, choices=RESULTS)
    datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.customer.name + ' ' + self.game or None