from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

class User(AbstractUser):
    pass

class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    seller_id = models.AutoField(primary_key=True)
    profile_picture = models.ImageField(upload_to="sellers/", default="default.jpg")
    mobile_no = models.CharField(max_length=10, unique=True)
    address = models.TextField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='seller_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='seller_updated_by')

    def __str__(self):
        return self.user.username
    
    def get_seller(self, obj):
        return obj.seller.user.username

class Buyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    buyer_id = models.AutoField(primary_key=True)
    profile_picture = models.ImageField(upload_to="buyers/", default="default.jpg")
    mobile_no = models.CharField(max_length=10, unique=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='buyer_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='buyer_updated_by')
    def __str__(self):
        return self.user.username

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=20, unique=True)
    category_detail = models.CharField(max_length=100, null = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'category_created_by', null = True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'category_updated_by', null = True)

    def __str__(self):
        return self.category_name

class SubCategory(models.Model):
    subcategory_id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory_name = models.CharField(max_length=50)
    subcategory_detail = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'subcategory_created_by', null = True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'subcategory_updated_by', null = True)

    class Meta:
        unique_together = ('category', 'subcategory_name')

    def __str__(self):
        return f"{self.category.category_name} - {self.subcategory_name}"

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    images = models.ImageField()
    price = models.DecimalField(max_digits=10, decimal_places=2,)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0.01)])
    quantity = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    brand = models.CharField(max_length=50)
    tags = models.CharField(max_length=255, blank=True)
    size = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=20, blank=True)
    fabric = models.CharField(max_length=50, blank=True)
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'product_created_by', null = True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'product_updated_by', null = True)

    def __str__(self):
        return self.name
    
class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    buyer = models.OneToOneField(Buyer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'cart_created_by', blank = True, null = True) 
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'cart_updated_by', blank = True, null = True) 

    def __str__(self):
        return f"Cart no. {self.cart_id} for {self.buyer.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    selected_color = models.CharField(max_length=50, blank=True)
    selected_size = models.CharField(max_length=50, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete= models.CASCADE, related_name = 'cart_items_created_by',null = True) 

    class Meta:
        unique_together = ('cart', 'product', 'selected_color', 'selected_size')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"    

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]
    
    order_id = models.AutoField(primary_key=True)
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, null=True)
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    dispatch_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    tracking_number = models.CharField(max_length=50, blank=True)
    shipping_company = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"Order #{self.order_number}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('COD', 'Cash on Delivery'),
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('NET_BANKING', 'Net Banking'),
        ('UPI', 'UPI'),
        ('WALLET', 'Wallet'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    payment_id = models.AutoField(primary_key=True)
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_date = models.DateTimeField(auto_now_add=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    refund_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment #{self.transaction_id}"
