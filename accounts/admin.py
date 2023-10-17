from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Customer)
admin.site.register(Tag)
admin.site.register(Product)
admin.site.register(Match)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(CartItem)
admin.site.register(Cart)
