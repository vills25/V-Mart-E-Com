from django.db import models

class BuyerRegistration(models.Model):
    buyer_id = models.AutoField(primary_key=True)
    buyer_name = models.CharField(max_length=50)
    buyer_email = models.EmailField(max_length=50, unique=True)
    buyer_image = models.ImageField(upload_to='buyers/',)
    buyer_ph_number = models.CharField(max_length=15)
    buyer_address = models.TextField(max_length=300,blank=True, null=True)
    buyer_password = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.buyer_name

# class SellerRegistration(models.Model):
#     seller_id = models.AutoField(primary_key=True)
#     seller_name = models.CharField(max_length=50)
#     seller_email = models.EmailField(max_length=50, unique=True)
#     seller_image = models.ImageField(upload_to='sellers/', blank=True, null=True)
#     seller_ph_number = models.CharField(max_length=15)
#     seller_address = models.TextField(max_length=300)
#     seller_password = models.CharField(max_length=15)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.seller_name

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
    # seller = models.ForeignKey(SellerRegistration, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=50)
    product_description = models.TextField(max_length=300)
    product_image = models.ImageField(upload_to='products/', blank=True, null=True)     
    product_category = models.ForeignKey(CategoryName, on_delete = models.CASCADE)
    product_subcategory = models.ForeignKey(SubCategory, on_delete = models.CASCADE)
    product_price = models.FloatField(default= 01.00)
    product_quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name

class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    buyer_cart_id = models.ForeignKey(BuyerRegistration, on_delete= models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
class CartItems(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart_id = models.ForeignKey(Cart, on_delete= models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

# class CheckOutPayment(models.Model):
#     buyer_id = models.ForeignKey(BuyerRegistration, on_delete=models.CASCADE)
#     cart_items = models.ForeignKey(CartItems, on_delete=models.CASCADE)
#     razorpay_order_id = models.CharField(max_length=100)
#     razorpay_payment_id = models.CharField(max_length=100)
#     amount = models.FloatField()
#     payment_verified = models.BooleanField(default=False)
    
#     def __str__(self):
#         return self.buyer_id.buyer_name  

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    buyer = models.ForeignKey(BuyerRegistration, on_delete=models.CASCADE)
    total_amount = models.FloatField()
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.order_id} by {self.buyer.buyer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.FloatField()  # snapshot of product price at order time

    def __str__(self):
        return f"{self.product.product_name} ({self.quantity})"
