# Create your views here.

from .models import CustomUser, Cart, CartItems, Product, CategoryName, SubCategory,Order, OrderItem
from .serializers import UserSerializer,CategoryNameSerializer,SubcategorySerializer,ProductSerializer,CartSerializer, CartItemsSerializer, OrderItemSerializer, OrderSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from django.db.models import Q
from rest_framework.generics import ListAPIView

# ----------------------------------
# Pagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 100

# Register Buyer View
@permission_classes([AllowAny])
@api_view(['POST'])
def register_view(request):
    serializer = UserSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Buyer registeration successfull", "Buyer": serializer.data},status=201)
    return Response({"message": "Failed", "error": serializer.errors}, status=400)


# #Login Buyer View
# @permission_classes([AllowAny])
# @api_view(['POST'])
# def login_view(request):
#     buyer_email = request.data.get("buyer_email")
#     print('-------------------->>>>>>>>>>>>>>>>>>>>>>>',buyer_email)
#     password = request.data.get("buyer_password")
#     print('-------------------->>>>>>>>>>>>>>>>>>>>>>>', password)
#     buyer = authenticate(username = buyer_email, password= password )
    
#     if buyer:
#         refresh = RefreshToken.for_user(buyer)
#         print('--------------------------')
#         return Response({
#             "refresh": str(refresh),
#             "access": str(refresh.access_token),
#             "user": BuyerRegistrationSerializer(buyer).data
#         }, status=200)
#     else:
#         return Response({"error": "Invalid login details"}, status=401)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
 
    print('----------->>>>>>>>>>>',username, password)
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        try:
            user = CustomUser.objects.get(username=username)
            print('------------->>>>>>>>>>>>',user)

            if user.check_password(password):
                user = authenticate(username=username, password=password)
            else:
                return Response({"error": "Invalid password"}, status=401)
        except CustomUser.DoesNotExist:
            return Response({"error": "Username not found"}, status=404)
    
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data
        })
    return Response({"error": "Authentication failed"}, status=401)

# Log-out view
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logout successful."}, status=205)
    except Exception as e:
        return Response({"error": "Invalid token"}, status=400)        
    
# ----------------------------------------------------------------------

# Fatch buyer Profile
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def buyer_profile_view(request):
    data = CustomUser.objects.all()
    serializer = UserSerializer(data, many=True)
    return Response({"message": "buyer Profile Fatched", "data": serializer.data}, status=200)

# Update Buyer Profile
@permission_classes([IsAuthenticated])
@api_view(['PUT','PATCH'])
def buyer_update(request):
    serializer = UserSerializer(CustomUser,data=request.data, partial=True )
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Buyer updated", "data": serializer.data}, status=200)
    return Response({"message": "Failed", "error": serializer.errors}, status=400)

# Delete Account/Profile View
@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def buyer_delete(request):
    buyer_id = request.data.get('id')
    if not buyer_id:
        return Response({"error": "enter buyer id please"}, status=400)
    try:
        buyer = CustomUser.objects.get(id=buyer_id)
        buyer.delete()
        return Response({"message": "Buyer deleted"}, status=200)
    except CustomUser.DoesNotExist:
        return Response({"error": "Buyer not found"}, status=404)

#Now Not Working
# Reset Password
@permission_classes([IsAuthenticated])
@api_view(['POST']) 
def     reset_password_view(request):
    buyer_email = request.data.get("email")
    if not buyer_email:
        return Response({"error": "Enter Email please"}, status=400) 
    try:
        buyer = CustomUser.objects.get(buyer_email=buyer_email)
    except CustomUser.DoesNotExist:
        return Response({"error": "Buyer not found"}, status=404)

#python django shell...    
# from myapp.models import CustomUser
# user = CustomUser.objects.get(username="testuser")
# user.set_password("new_password")
# user.save()    

# ----------------------------------------------------------------------
# Category CRUD

# Pegination
class CategoryListView(ListAPIView):
    queryset = CategoryName.objects.all()
    serializer_class = CategoryNameSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter]
    search_fields = ['category_name']

# category Create
@permission_classes([IsAdminUser])
@api_view(['POST'])
def category_create(request):
    serializer = CategoryNameSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"Message": "Category Created", "category": serializer.data}, status=201)
    return Response({"message": "Failed", "error": serializer.errors}, status=400)

#catagory get
@permission_classes([AllowAny])
@api_view(['GET'])
def category_view(request):
    data = CategoryName.objects.all()
    serializer = CategoryNameSerializer(data, many = True)
    return Response({"Message": "Data Fatched", "Category": serializer.data})

# Category Update
@permission_classes([IsAdminUser])
@api_view(['PUT'])
def category_update(request):
    serializer = CategoryNameSerializer(CategoryName, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Category updated", "Updated Category": serializer.data}, status=200)
    return Response({"message": "Failed", "error": serializer.errors}, status=400)

# Category Delete
@permission_classes([IsAdminUser])
@api_view(['DELETE'])
def category_delete(request):
    category_id = request.data.get("id")
    if not category_id:
        return Response({"error": "enter category id please"}, status=400)
    try:
        category = CategoryName.objects.get(id=category_id)
        category.delete()
        return Response({"message": "Category deleted"}, status=200)
    except CategoryName.DoesNotExist:
        return Response({"error": "Category not found"}, status=404)

# ----------------------------------------------------------------------
# Subcategory CRUD

# Pagination
class SubCategoryListView(ListAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubcategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter]
    search_fields = ['sub_category_name']

# Subcategory Create
@permission_classes([IsAdminUser])
@api_view(['POST'])
def subcategory_create(request):
    serializer = SubcategorySerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"Message":"Created success", "data":serializer.data}, status=201)
    else: 
        return Response({"Error": serializer.errors})

# Subcategory GET
@permission_classes([AllowAny])
@api_view(['GET'])
def subcategory_view(request):
    data = SubCategory.objects.all()
    serializer = SubcategorySerializer(data, many = True)
    return Response({"Message":"Fatched", "Data": serializer.data}, status = 200)

# Sub category Update & Delete
@permission_classes([IsAdminUser])
@api_view(['PUT', 'DELETE'])
def subcategory_update_delete(request):
    get_subcategory_id = request.data.get('id')
    
    if request.method == 'PUT':
        serializer = SubcategorySerializer(SubCategory, get_subcategory_id, data = request.data, partial = True)
        if serializer.is_valid:
            serializer.save()
            return Response({"Message": "Sub category updated", "Data": serializer.data}, status=201)
        return Response({"Message" : "failde", "error": serializer.errors}, status=400)
    
    elif request.method == 'DELETE':
        subcategory = SubCategory.objects.get(id = get_subcategory_id)
        subcategory.delete()
        return Response({"Message": "Deleted success"}, status=200)

# ----------------------------------------------------------------------
# Product CRUD

# Pagination
class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter]
    search_fields = ['product_name', 'product_description']

#Product Create 
@permission_classes([IsAdminUser])
@api_view(['POST'])
def product_create(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Product Created", "data": serializer.data}, status=201)
    return Response({"message": "Failed", "error": serializer.errors}, status=404)

#Product GET
@permission_classes([AllowAny])
@api_view(['GET'])
def product_get(request):
    data = Product.objects.all()
    serializer = ProductSerializer(data, many=True)
    return Response({"message": "Fatched", "data": serializer.data}, status=200)

# Product update 
@permission_classes([IsAdminUser])
@api_view(['PUT'])
def product_update(request):
    product_id = request.data.get('id')
    serializer = ProductSerializer(Product, product_id, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Product updated", "data": serializer.data}, status=200)
    return Response({"message": "Failed", "error": serializer.errors}, status=400)

# Product Delete
@permission_classes([IsAdminUser])
@api_view(['DELETE'])
def product_delete(request):
    product_id = request.data.get('id')
    if not product_id:
        return Response({"Message": "Enter valid id"}, status=400)
    try:
        product = Product.objects.get(id = product_id)
        product.delete()
    except Product.DoesNotExist:
        return Response({"Message": "product not found"}, status=404)

#--------------------------------------------------------------------------
# Cart CRUD

# Cart Get
@permission_classes([IsAuthenticated, IsAdminUser])
@api_view(['GET'])
def cart_get(request):
    cart_data = Cart.objects.all()
    print('--------------->>>>>>>>>>>>>>',cart_data)
    serializer = CartSerializer(cart_data, many = True)
    return Response({"Message": " Cart Fatched", "Cart": serializer.data},status=200)

# Cart Add
@permission_classes([IsAdminUser, IsAuthenticated])
@api_view(['POST'])
def cart_create(request):
    serializer = CartSerializer(data = request.data)
    print('--------------->>>>>>>>>>>>>>',serializer)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Cart added", "data": serializer.data}, status=201)
    return Response({"message": "Failed", "error": serializer.errors}, status=400)

# Cart Update & Delete
@permission_classes([IsAuthenticated,IsAdminUser])
@api_view(['PUT', 'DELETE'])
def cart_update_delete(request):
    cart_id = request.data.get('id')

    if request.method == 'PUT':
        serializer = CartSerializer(Cart, cart_id, data = request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response({"Messsage": "Update Success", "Updated Data": serializer.data}, status=201)
        return Response({"Message": "Faile", "error": serializer.errors}, status=400)
    
    if request.method == 'DELETE':
        cart = Cart.objects.get(id = cart_id)
        cart.delete()
        return Response({"Message": "Delete success"}, status=200)

#--------------------------------------------------------------------------

# Cartitems

class CartItemsListView(ListAPIView):
    queryset = CartItems.objects.all()
    serializer_class = CartItemsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter]
    search_fields = ['product_id__product_name']

#Cart Items Get
@permission_classes([IsAuthenticated, IsAdminUser])
@api_view(['GET'])
def cart_items_get(request):
    cart_items_data = CartItems.objects.all()
    serializer = CartItemsSerializer(cart_items_data, many = True)
    return Response({"Message":"Fatched success", "Cart Items": serializer.data}, status=200)

# Cart items Create
@permission_classes([IsAuthenticated, IsAdminUser])
@api_view(['POST'])
def cart_items_create(request):
    serializer = CartItemsSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Cart Items added in cart", "cart items": serializer.data}, status=201)
    return Response({"message": "Failed", "error": serializer.errors}, status=400)

# Cart Items Update & Delete
@permission_classes([IsAuthenticated,IsAdminUser])
@api_view(['PUT', 'DELETE'])
def cart_items_update_delete(request):
    cart_items_id = request.data.get('id')

    if request.method == 'PUT':
        serializer = CartItemsSerializer(CartItems, cart_items_id, data = request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response({"Messsage": "Update Success", "Updated cart items Data": serializer.data}, status=201)
        return Response({"Message": "Faile", "error": serializer.errors}, status=400)
    
    if request.method == 'DELETE':
        cart = CartItems.objects.get(id = cart_items_id)
        cart.delete()
        return Response({"Message": "Delete success"}, status=200)

#--------------------------------------------------------------------------

# Cancel Order view
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def cancel_order(request):
    order_id = request.data.get('order_id')
    try:
        order = Order.objects.get(order_id=order_id, buyer=request.user)
        if order.status == 'Cancelled':
            return Response({"message": "Order already cancelled"})
        order.status = 'Cancelled'
        order.save()
        return Response({"message": "Order cancelled successfully"})
    except Order.DoesNotExist:
        return Response({"error": "Order not exist"}, status=404)

#--------------------------------------------------------------------------

# get all buyer's(User's) orders
@permission_classes([IsAdminUser])
@api_view(['GET'])
def grt_all_orders_view(request):
    data = Order.objects.all()
    serializer = OrderSerializer(data, many=True)
    return Response({"orders": serializer.data})

#--------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout_view(request):
    buyer = request.user
    try:
        cart = Cart.objects.get(buyer=buyer)
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=404)

    cart_items = CartItems.objects.filter(cart = cart)
    if not cart_items.exists():
        return Response({"error": "Cart is empty"}, status=400)

    total_amount = sum(item.product_id.product_price * item.quantity for item in cart_items)
    
    # Create Order
    order = Order.objects.create(
        buyer=buyer,
        total_amount=total_amount,
        status='Pending'
    )
    
    # Create OrderItems
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product_id,
            quantity=item.quantity,
            price=item.product_id.product_price
        )
    
    # Clear cart
    cart_items.delete()
    return Response({"message": "Order created!", "total_amount": total_amount})
