
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

class ProductSerializer(serializers.ModelSerializer):
    seller_id = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['product_id', 'seller_id', 'name', 'description', 'price', 'sale_price', 'quantity', 'brand', 'tags','size','color','fabric','in_stock', 'created_at', 'created_by', 'updated_at', 
                  'updated_by', 'review_count', 'average_rating' ]
    
    def get_review_count(self, obj):
        return obj.productreview_set.count()
        
    def get_average_rating(self, obj):
        from django.db.models import Avg
        return obj.productreview_set.aggregate(Avg('rating'))['rating__avg'] or 0

    def get_seller_id(self, obj):
        return obj.seller.seller_id if obj.seller else None

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['cart_id', 'buyer', 'created_at', 'updated_at']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'selected_color', 'selected_size', 'total_price']

    def get_total_price(self, obj):
        price = obj.product.sale_price if obj.product.sale_price else obj.product.price
        return str(price * obj.quantity)


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'color', 'size', 'delivery_address', 'delivery_contact']

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
                   'shipping_company', 'notes', 'items', 'refund_status', 'refund_reason', 'refund_response', 'refund_date']

class OrderDetailSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['order_id', 'order_number', 'status', 'total', 'order_date', 'dispatch_date', 'delivery_date', 'tracking_number', 
                 'shipping_company', 'items']
        
    def get_items(self, obj):
        items = obj.items.all()
        return OrderItemSerializer(items, many=True).data

class SellerProductSerializer(serializers.ModelSerializer):
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['product_id', 'name', 'price', 'sale_price', 'quantity', 'in_stock', 'is_active', 'review_count', 'average_rating']
        read_only_fields = fields

class ProductReviewSerializer(serializers.ModelSerializer):
    buyer = BuyerSerializer()
    product = ProductSerializer()
    
    class Meta:
        model = ProductReview
        fields = ['product_review_id', 'product', 'buyer', 'rating', 'comment', 'created_at', 'updated_at']
        # read_only_fields = fields

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['wishlist_id', 'buyer', 'product', 'added_at', 'added_by']

class Forgot_password_otp_serializer(serializers.ModelSerializer):
    class Meeta:
        model = Forgot_password_otp
        fields = '__all__'        
