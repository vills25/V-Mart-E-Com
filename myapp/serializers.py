from rest_framework import serializers
from .models import BuyerRegistration, SellerRegistration, CategoryName,SubCategory , Product, Cart, CartItems

class BuyerRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyerRegistration
        fields = '__all__'

class SellerRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerRegistration
        fields = '__all__'

class CategoryNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryName
        fields = '__all__'

class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__' 

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

class CartItemsSerializer (serializers.ModelSerializer):
    class Meta:
        model = CartItems
        fields = '__all__'       