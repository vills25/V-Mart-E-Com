from django.contrib import admin
from .models import Seller, Buyer, Category, SubCategory, Product, Order, OrderItem, Payment, User, Cart, CartItem, ProductReview, Wishlist , Forgot_password_otp

admin. site.site_header = "V-Mart-Ecom Admin Corner"

# Apply Search For Fields in Models 

class UserAddSearchBar(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_superuser', 'is_active')
    search_fields = ['username']

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'brand','category', 'quantity', 'in_stock', 'is_active')
    search_fields = ['name','product_id']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id','category_name', 'category_detail')
    search_fields = ['category_name','category_id']

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('subcategory_id','subcategory_name','category')
    search_fields = ['subcategory_name','subcategory_id']

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'order_number', 'status', 'buyer', 'payment')
    search_fields = ['order_number','order_id']

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'color', 'size')
    search_fields = ['order']

class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'buyer')
    search_fields = ['cart_id','buyer']        

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'added_by')
    search_fields = ['cart','product']

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'status', 'amount', 'buyer', 'payment_date')
    search_fields = ['payment_id', 'buyer', 'status']

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product_review_id', 'product', 'buyer', 'rating')
    search_fields = ['buyer','product']

class WishlistAdmin(admin.ModelAdmin):
    list_display = ('wishlist_id', 'product', 'buyer')
    search_fields = ['buyer','product']
    
class BuyerAdmin(admin.ModelAdmin):
    list_display = ('user', 'buyer_id')
    search_fields = ['user', 'buyer_id']

class SellerAdmin(admin.ModelAdmin):
    list_display = ('user', 'seller_id', 'is_verified')
    search_fields = ['user','seller_id']

admin.site.register(Buyer, BuyerAdmin)
admin.site.register(Seller, SellerAdmin)
admin.site.register(User, UserAddSearchBar)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory,SubCategoryAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Payment,PaymentAdmin)
admin.site.register(Cart,CartAdmin )
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(ProductReview,ProductReviewAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Forgot_password_otp)
