from django.contrib import admin
from .models import Seller, Buyer, Category, SubCategory
# Register your models here.
admin.site.register(Buyer)
admin.site.register(Seller)
admin.site.register(Category)
admin.site.register(SubCategory)
