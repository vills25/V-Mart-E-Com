from django.contrib import admin
from .models import Seller, Buyer, Category, SubCategory, Product, Order, OrderItem, Payment, User, Cart, CartItem
# Register your models here.
admin.site.register(User)
admin.site.register(Buyer)
admin.site.register(Seller)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Cart)
admin.site.register(CartItem)

