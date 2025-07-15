# from rest_framework import serializers
# from .models import CustomUser, CategoryName,SubCategory , Product, Cart, CartItems, OrderItem, Order, Wishlist, UserAddress, ProductReview

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ['id', 'username', 'email','password', 'ph_number', 'address', 'image']

#     def create(self, validated_data):
#         user = CustomUser.objects.create_user(
#             username=validated_data['username'],
#             password=validated_data['password'],
#             email=validated_data.get('email', ''))
#         return user

# class RegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ['username', 'email', 'password','ph_number', 'address', 'image']

# class UserAddressSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserAddress
#         fields = '__all__'
#         read_only_fields = ('user', 'created_at')

# class CategoryNameSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CategoryName
#         fields = ['category_id', 'category_name', 'category_detail']

# class SubcategorySerializer(serializers.ModelSerializer):
#     categorey_name = serializers.CharField(source='category.category_name', read_only=True)
#     class Meta:
#         model = SubCategory
#         fields = ['sub_category_id', 'sub_category_name', 'category', 'category_name']

# class ProductSerializer(serializers.ModelSerializer):
#     product_category_name = serializers.CharField(source='product_category.category_name',read_only = True)
#     product_subcategory_name = serializers.CharField(source='product_subcategory.sub_category_name', read_only = True)
#     class Meta:
#         model = Product
#         fields = '__all__' 

# class CartSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Cart
#         fields = ['cart_id', 'buyer', 'created_at']

# class CartItemsSerializer (serializers.ModelSerializer):
#     product_name = serializers.CharField(source='product.product_name', read_only = True)
#     class Meta:
#         model = CartItems
#         fields = ['id', 'product_id', 'product_name', 'cart', 'quantity']       

# class OrderSerializer (serializers.ModelSerializer):
#     class Meta:
#         model = Order
#         fields = '__all__'

# class OrderItemSerializer(serializers.ModelSerializer):
#     product_name = serializers.CharField(source='product.product_name',read_only = True)
#     class Meta:
#         model = OrderItem
#         fields = ['id', 'product', 'product_name', 'quantity', 'price']

# class WishlistSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Wishlist
#         fields = ['wishlist_id', 'user', 'product','added_at']

# class ReviewSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductReview
#         fields =  ['id', 'user', 'product', 'rating', 'review_text', 'created_at', 'created_by']      

from rest_framework import serializers
from .models import Seller, Buyer, Category, SubCategory

class BuyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buyer
        fields = ['buyer_id', 'username','first_name', 'last_name', 'email','password', 'profile_picture','mobile_no', 'address']

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ['seller_id','username','first_name', 'last_name', 'email','password', 'profile_picture', 'mobile_no', 'address']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id', 'category_name', 'category_detail']

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['sub_category_id', 'sub_category_name', 'category']
