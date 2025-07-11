from django.contrib import admin
from .models import CustomUser, CategoryName,SubCategory , Product, Cart, CartItems,Order,OrderItem, Wishlist
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(CategoryName)
admin.site.register(SubCategory)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItems)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Wishlist)