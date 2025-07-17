
from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
  
class SellerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Seller
        fields = ['seller_id', 'user', 'profile_picture', 'mobile_no', 'address', 'is_verified', 'created_at', 'updated_at', 'created_by', 'updated_by']

class BuyerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Buyer
        fields = ['buyer_id', 'user', 'profile_picture', 'mobile_no', 'address','created_at', 'updated_at', 'created_by', 'updated_by']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id', 'category_name', 'category_detail', 'created_at', 'updated_at', 'created_by', 'created_by']

class SubCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    
    class Meta:
        model = SubCategory
        fields = ['subcategory_id', 'subcategory_name', 'subcategory_detail' , 'category', 'created_at', 'updated_at', 'created_by', 'created_by']

# class ProductSerializer(serializers.ModelSerializer):
#     seller = SellerSerializer()
#     class Meta:
#         model = Product
#         # fields = ['product_id', 'seller', 'name', 'description', 'images' ,'price', 'sale_price', 'quantity', 'category', 'sub_category',
#         #           'brand', 'tags', 'size', 'color', 'fabric', 'in_stock','is_active', 'created_at', 'updated_at', 'created_by', 'created_by']
#         fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    seller_id = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['product_id', 'seller_id', 'name', 'description', 'price', 
                 'sale_price', 'quantity', 'brand', 'in_stock', 'created_at', 'created_by', 'updated_at','updated_by']
    
    def get_seller_id(self, obj):
        return obj.seller.seller_id if obj.seller else None
    
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'color', 'size']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['payment_id', 'amount', 'payment_method', 'transaction_id', 'status', 'payment_date', 'refund_amount', 'refund_date']
class OrderSerializer(serializers.ModelSerializer):
    buyer = BuyerSerializer()
    payment = PaymentSerializer()
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ['order_id', 'order_number', 'buyer', 'payment', 'status','total', 'order_date', 'dispatch_date', 'delivery_date','tracking_number', 
                   'shipping_company', 'notes', 'items']

class OrderDetailSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['order_id', 'order_number', 'status', 'total', 'order_date', 'dispatch_date', 'delivery_date', 'tracking_number', 
                 'shipping_company', 'items']
class ProductListSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.user.username')
    main_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['product_id', 'name', 'price', 'sale_price', 'main_image', 'seller_name', 'in_stock', 'category', 'sub_category']
        read_only_fields = fields

class OrderSummarySerializer(serializers.ModelSerializer):
    item_count = serializers.SerializerMethodField()
    first_product = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['order_id', 'order_number', 'status', 'total', 'order_date', 'item_count', 'first_product']
        read_only_fields = fields

class SellerProductSerializer(serializers.ModelSerializer):
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['product_id', 'name', 'price', 'sale_price', 'quantity', 'in_stock', 'is_active', 'review_count', 'average_rating']
        read_only_fields = fields
