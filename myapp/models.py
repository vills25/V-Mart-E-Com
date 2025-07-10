from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ph_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(max_length=300, blank=True, null=True)
    image = models.ImageField(upload_to='users/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.username

class CategoryName(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category_name

class SubCategory(models.Model):
    sub_category_id = models.AutoField(primary_key=True)
    sub_category_name = models.CharField(max_length=30)
    category = models.ForeignKey(CategoryName, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) :
        return self.sub_category_name

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=50)
    product_description = models.TextField(max_length=300)
    product_image = models.ImageField(upload_to='products/', blank=True, null=True)     
    product_category = models.ForeignKey(CategoryName, on_delete = models.CASCADE)
    product_subcategory = models.ForeignKey(SubCategory, on_delete = models.CASCADE)
    product_price = models.FloatField(default= 0.0)
    product_quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name

class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.buyer.username

class CartItems(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)  
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)  
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return self.cart.buyer.username

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    ORDER_STATUS = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  
    total_amount = models.FloatField()
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order for {self.buyer.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.FloatField()

    def __str__(self):
        return f"{self.product.product_name} x {self.quantity}"
