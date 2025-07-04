from django.contrib import admin
from .models import BuyerRegistration, SellerRegistration, CategoryName,SubCategory , Product, Cart, CartItems
# Register your models here.

admin.site.register(BuyerRegistration)
admin.site.register(SellerRegistration)
admin.site.register(CategoryName)
admin.site.register(SubCategory)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItems)
