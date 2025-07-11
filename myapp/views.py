# Create your views here.

from .models import CustomUser, Cart, CartItems, Product, CategoryName, SubCategory,Order, OrderItem, Wishlist
from .serializers import UserSerializer,CategoryNameSerializer,RegisterSerializer,SubcategorySerializer,ProductSerializer,CartSerializer, CartItemsSerializer, OrderItemSerializer, OrderSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .serializers import ProductSerializer

# ----------------------------------
# Pagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'

# Register Buyer View
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Buyer registeration successfull", "Buyer": serializer.data},status=201)
    return Response({"message": "Failed", "error": serializer.errors}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    
    if user is None:
        try:
            user = CustomUser.objects.get(username=username)
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
            "user": UserSerializer(user).data })
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

# Search Buyer & Pagination
@api_view(['POST'])
def search_buyer(request):
    search_query = request.data.get('username', '')
    buyer = CustomUser.objects.filter(Q(username__icontains=search_query))
    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(buyer, request)
    serializer = UserSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

# Fatch buyer Profile
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buyer_profile_view(request):
    data = CustomUser.objects.all()
    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(data, request)
    serializer = UserSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

# Update Buyer Profile
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def buyer_update(request):
    buyer_id = request.data.get('buyer_id')
    try:
        buyer = CustomUser.objects.get(id=buyer_id)
    except CustomUser.DoesNotExist:
        return Response({"error": "Buyer not found"}, status=404)

    serializer = UserSerializer(buyer, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Buyer updated", "data": serializer.data}, status=200)
    return Response({"message": "Failed", "error": serializer.errors}, status=400)

# Delete Account/Profile View
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
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

# Forgot Password 
@api_view(['POST'])
@permission_classes([AllowAny]) 
def forgot_password_view(request):
    buyer_email = request.data.get("email")
    new_password = request.data.get("new_password")
    
    if not buyer_email or not new_password:
        return Response({"error": "Enter email and new password please!!"}, status=400)
    try:
        buyer = CustomUser.objects.get(email__iexact=buyer_email)
        buyer.set_password(new_password)
        buyer.save()
        return Response({"message": "Password Update Success"}, status=200)
    except CustomUser.DoesNotExist:
        return Response({"error": "Buyer not exist"}, status=404)

# ----------------------------------------------------------------------
# Category CRUD

# Pegination
@api_view(['POST'])
def search_category(request):
    search_query = request.data.get('category_name', '')
    category = CategoryName.objects.filter(Q(category_name__icontains=search_query)| Q(category_id__icontains=search_query) ) 
    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(category, request)
    serializer = CategoryNameSerializer(result_page, many=True)
  
    return paginator.get_paginated_response(serializer.data)     

# category Create
@api_view(['POST'])
@permission_classes([IsAdminUser])
def category_create(request):
    serializer = CategoryNameSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"Message": "Category Created", "category": serializer.data}, status=201)
    return Response({"message": "Failed", "error": serializer.errors}, status=400)

#catagory get
@api_view(['GET'])
@permission_classes([AllowAny])
def category_view(request):
    data = CategoryName.objects.all()
    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(data, request)
    serializer = CategoryNameSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

# Category Update
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def category_update(request):
    category_id = request.data.get("id")
    try:
        category = CategoryName.objects.get(id=category_id)
    except CategoryName.DoesNotExist:
        return Response({"error": "Category not found"}, status=404)

    serializer = CategoryNameSerializer(category, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Category updated", "Updated Category": serializer.data}, status=200)
    return Response({"message": "Failed", "error": serializer.errors}, status=400)

# Category Delete
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
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
@api_view(['POST'])
def search_subcategory(request):
    search_query = request.data.get('sub_category_name', '')
    subcategory = SubCategory.objects.filter(Q(sub_category_name__icontains=search_query))
    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(subcategory, request)
    serializer = SubcategorySerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)      

# Subcategory Create
@api_view(['POST'])
@permission_classes([IsAdminUser])
def subcategory_create(request):
    serializer = SubcategorySerializer(data = request.data, many= True)
    if serializer.is_valid():
        serializer.save()
        return Response({"Message":"Created success", "data":serializer.data}, status=201)
    else: 
        return Response({"Error": serializer.errors})

# Subcategory GET
@api_view(['GET'])
@permission_classes([AllowAny])
def subcategory_view(request):
    data = SubCategory.objects.all()
    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(data, request)
    serializer = SubcategorySerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

# Sub category Update & Delete
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def subcategory_update_delete(request):
    get_subcategory_id = request.data.get('id')

    try:
        subcategory = SubCategory.objects.get(id=get_subcategory_id)
    except SubCategory.DoesNotExist:
        return Response({"error": "Subcategory not found"}, status=404)

    if request.method == 'PUT':
        serializer = SubcategorySerializer(subcategory, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"Message": "Sub category updated", "Data": serializer.data}, status=200)
        return Response({"Message": "Failed", "error": serializer.errors}, status=400)

    elif request.method == 'DELETE':
        subcategory.delete()
        return Response({"Message": "Deleted successfully"}, status=200)

# ----------------------------------------------------------------------
# Product CRUD

# Product Search & Pegination
@api_view(['POST'])
def search_product(request):
    search_query = request.data.get('product_name','')
    products = Product.objects.filter(
        Q(product_name__contains=search_query) |
        Q(product_description__contains=search_query))    
     
    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(products, request)
    serializer = ProductSerializer(result_page, many=True)

    return paginator.get_paginated_response(serializer.data)    

#Product Create 
@api_view(['POST'])
@permission_classes([IsAdminUser])
def product_create(request):
    serializer = ProductSerializer(data=request.data, many = True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Product Created", "data": serializer.data}, status=201)
    return Response({"message": "Failed", "error": serializer.errors}, status=404)

#Product GET
@api_view(['GET'])
@permission_classes([AllowAny])
def product_get(request):
    data = Product.objects.all()
    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(data, request)
    serializer = ProductSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

# Product update 
@api_view(['PATCH', 'PUT'])
@permission_classes([IsAdminUser])
def product_update(request):
    product_id = request.data.get('product_id')
    try:
        product = Product.objects.get(product_id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    serializer = ProductSerializer(product, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Product updated", "data": serializer.data}, status=200)
    return Response({"message": "Failed", "error": serializer.errors}, status=400)

# Product Delete
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
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
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def cart_get(request):
    cart_data = Cart.objects.all()
    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(cart_data, request)
    serializer = CartSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

# Cart Add
@api_view(['POST'])
@permission_classes([IsAdminUser, IsAuthenticated])
def cart_create(request):
    serializer = CartSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Cart added", "data": serializer.data}, status=201)
    return Response({"message": "Failed", "error": serializer.errors}, status=400)

# Cart Update & Delete
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def cart_update_delete(request):
    cart_id = request.data.get('id')
    try:
        cart = Cart.objects.get(id=cart_id)
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=404)

    if request.method == 'PUT':
        serializer = CartSerializer(cart, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"Messsage": "Update Success", "Updated Data": serializer.data}, status=200)
        return Response({"Message": "Failed", "error": serializer.errors}, status=400)

    if request.method == 'DELETE':
        cart.delete()
        return Response({"Message": "Delete success"}, status=200)

#--------------------------------------------------------------------------
# Cartitems

# Cart Items Search & Paginations
@api_view(['POST'])
def search_cart_items(request):
    search_query = request.data.get('product_name', 'product_id', '')
    cart_items = CartItems.objects.filter(
        Q(product_name__icontains=search_query) |
        Q(product_id__icontains=search_query))

    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(cart_items, request)
    serializer = CartItemsSerializer(result_page, many=True)

    return paginator.get_paginated_response(serializer.data)

#Cart Items Get
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def cart_items_get(request):
    cart_items_data = CartItems.objects.all()
    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(cart_items_data, request)
    serializer = CartItemsSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

# Cart items Create
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def cart_items_create(request):
    serializer = CartItemsSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Cart Items added in cart", "cart items": serializer.data}, status=201)
    return Response({"message": "Failed", "error": serializer.errors}, status=400)

# Cart Items Update & Delete
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def cart_items_update_delete(request):
    cart_items_id = request.data.get('id')
    try:
        cart_item = CartItems.objects.get(id=cart_items_id)
    except CartItems.DoesNotExist:
        return Response({"error": "Cart Item not found"}, status=404)

    if request.method == 'PUT':
        serializer = CartItemsSerializer(cart_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"Messsage": "Update Success", "Updated cart items Data": serializer.data}, status=200)
        return Response({"Message": "Failed", "error": serializer.errors}, status=400)

    if request.method == 'DELETE':
        cart_item.delete()
        return Response({"Message": "Delete success"}, status=200)

#--------------------------------------------------------------------------

# Cancel Order view
@api_view(['POST'])
@permission_classes([IsAuthenticated])
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

# get all orders
@api_view(['GET'])
@permission_classes([IsAdminUser])
def grt_all_orders_view(request):
    data = Order.objects.all()
    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(data, request)
    serializer = OrderSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

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
        status='Pending')
    
    # Create OrderItems
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product_id,
            quantity=item.quantity,
            price=item.product_id.product_price)
    # Clear cart
    cart_items.delete()
    return Response({"message": "Order created!", "total_amount": total_amount})

#--------------------------------------------------------------------------
# Wishlist

@api_view(['GET', 'POST', 'DELETE'])
def whishlist_add_get_remove(request):
    user = request.user

    if request.method == 'GET':
        wish_items = Wishlist.objects.filter(user=user)
        products = [item.product for item in wish_items]
        serializer = ProductSerializer(products, many=True)
        return Response({"Message": "Fetch Success ","wishlist": serializer.data})

    elif request.method == 'POST':
        product_id = request.data.get('product_id')
        try:
            if product_id:
                product = Product.objects.get(product_id=product_id)
            else:
                return Response({"error": "Enter product_id"}, status=400)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)
        
        if Wishlist.objects.create(user=user, product=product):
            return Response({"message": "Success product added to wishlist"}, status=201)

    elif request.method == 'DELETE':
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({"Message": "Enter valid id"}, status=400)
        try:
            product = Wishlist.objects.get(product_id = product_id)
            product.delete()
            return Response({"message": " Delete Success "}, status = 200)
        except Wishlist.DoesNotExist:
            return Response({"Message": "product not found"}, status=404)
        
