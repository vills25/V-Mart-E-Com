from rest_framework import serializers
from .models import CustomUser, CategoryName,SubCategory , Product, Cart, CartItems, OrderItem, Order

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email','password', 'ph_number', 'address', 'image']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''))
        return user

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']

class CategoryNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryName
        fields = '__all__'

class SubcategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    class Meta:
        model = SubCategory
        fields = ['sub_category_id', 'sub_category_name', 'category', 'category_name']

class ProductSerializer(serializers.ModelSerializer):
    product_category_name = serializers.CharField(source='product_category.category_name',read_only = True)
    product_subcategory_name = serializers.CharField(source='product_subcategory.sub_category_name', read_only = True)
    class Meta:
        model = Product
        fields = '__all__' 

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['cart_id', 'buyer', 'created_at']

class CartItemsSerializer (serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only = True)
    class Meta:
        model = CartItems
        fields = ['id', 'product_id', 'product_name', 'cart', 'quantity']       

class OrderSerializer (serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name',read_only = True)
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']

