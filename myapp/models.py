from django.db import models
from django.contrib.auth.models import AbstractUser

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
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_updated_by')

    def __str__(self):
        return self.user.username

class Buyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    buyer_id = models.AutoField(primary_key=True)
    profile_picture = models.ImageField(upload_to="buyers/", default="default.jpg")
    mobile_no = models.CharField(max_length=10, unique=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_updated_by')
    def __str__(self):
        return self.user.username

class Category(models.Model):
    category_id = models.AutoField()
    category_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'category_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'category_updated_by')

    def __str__(self):
        return self.category_name

class SubCategory(models.Model):
    subcategory_id = models.AutoField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'subcategory_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'subcategory_updated_by')

    class Meta:
        unique_together = ('category', 'name')

    def __str__(self):
        return f"{self.category.category_name} - {self.subcategory_name}"
