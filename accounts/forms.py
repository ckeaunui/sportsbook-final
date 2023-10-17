from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *


class OrderForm (ModelForm):
    class Meta:
        model = Order
        fields = ['price', 'wager', 'to_win', 'status']
        
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class EditUserForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'credit', 'balance', 'freeplay']

class CreateOrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['wager']


