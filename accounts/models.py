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
    name = models.CharField(max_length=200, null=True)

    def __str__(self):
	    return self.name or None


class Match(models.Model):
    match_id = models.CharField(max_length=150, null=True)
    league  = models.CharField(max_length=150, null=True)
    sport_title  = models.CharField(max_length=150, null=True)
    match_name = models.CharField(max_length=200, null=True)
    team1 = models.CharField(max_length=200, null=True)
    team2 = models.CharField(max_length=200, null=True)
    commence_time = models.CharField(max_length=50, null=True)

    def __str__(self):
	    return self.match_name or 'name'


class Product(models.Model):
    KEYS = (
        ('h2h', 'h2h'),
        ('spreads', 'spreads'),
        ('totals', 'totals')
    )

    match = models.ForeignKey(Match, null=True, related_name="children", on_delete=models.CASCADE)
    key = models.CharField(max_length=100, null=True, choices=KEYS)
    winner = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=100, null=True)  
    display_data = models.CharField(max_length=100, null=True)  
    price = models.IntegerField(null=True)
    point = models.FloatField(null=True)
    max_wager = models.FloatField(null=True)
    
    def __str__(self):
	    return (self.key + " " + self.winner) or None


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    credit = models.FloatField(default=0.0, null=True)
    balance = models.FloatField(default=0.0, null=True)
    pending = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)], null=True)
    freeplay = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)], null=True)

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
    name = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=200, null=True)
    price = models.IntegerField(null=True)
    wager = models.FloatField(validators=[MinValueValidator(0.0)], null=True)
    to_win = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5_000.0)], null=True)
    status = models.CharField(max_length=50, default='Pending', null=True, choices=STATUSES)
    products = models.ManyToManyField(OrderItem, blank=True, related_name='products')
    date_ordered = models.DateTimeField(auto_now=True)
    payment_method = models.CharField(max_length=100, default='Credit', choices=PAYMENT_METHODS)

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
    wager_type = models.CharField(max_length=100, null=True, default='Straight', choices=WAGER_TYPES)

    def __str__(self):
        return self.product.winner or None

