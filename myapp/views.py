# Create your views here.

from rest_framework import decorators
from .models import BuyerRegistration, Cart, CartItems, Product, SellerRegistration, CategoryName, SubCategory
from .serializers import BuyerRegistrationSerializer,SellerRegistrationSerializer,CategoryNameSerializer,SubcategorySerializer,ProductSerializer,CartSerializer, CartItemsSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

# Register Buyer View
@permission_classes([AllowAny])
@api_view(['POST'])
def register_view(request):
    serializer = BuyerRegistrationSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Buyer registeration successfull", "Buyer": serializer.data},status=201)
    return Response({"message": "Failed", "error": serializer.errors}, status=400)


#Login Buyer View
@permission_classes([AllowAny])
@api_view(['POST'])
def login_view(request):
    buyer_email = request.data.get("email")
    password = request.data.get("password")
    buyer = authenticate(buyer_email=buyer_email, password=password)

    if buyer:
        refresh = RefreshToken.for_user(buyer)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": BuyerRegistrationSerializer(buyer).data
        }, status=200)
    else:
        return Response({"error": "Invalid login details"}, status=401)


# Fatch User Profile
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def user_profile_view(request):
    data = BuyerRegistration.objects.all()
    serializer = BuyerRegistrationSerializer(data, many=True)
    return Response({"message": "User Profile Fatched", "data": serializer.data}, status=200)

# Update user Profile
@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def user_update(request):
    serializer = BuyerRegistrationSerializer(BuyerRegistration,data=request.data, partial=True )
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User updated", "data": serializer.data}, status=200)
    return Response({"message": "Failed", "error": serializer.errors}, status=400)

# Reset Password
@permission_classes([IsAuthenticated])
@api_view(['POST']) 
def reset_password_view(request):
    buyer_email = request.data.get("email")
    if not buyer_email:
        return Response({"error": "Enter Email please"}, status=400) 
    try:    
        buyer = BuyerRegistration.objects.get(buyer_email=buyer_email)
    except BuyerRegistration.DoesNotExist:
        return Response({"error": "Buyer not found"}, status=404)
    
# category Create
@permission_classes([IsAdminUser])
@api_view(['POST'])
def caegory_create(request):
    serializer = CategoryNameSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"Message": "Category Created"}, status=201)
    return Response(serializer.error_messages)

#catagero get

# Category Update
@permission_classes([IsAdminUser])
@api_view(['PUT'])
def category_update(request):
    serializer = CategoryNameSerializer(CategoryName, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Category updated", "data": serializer.data}, status=200)
    return Response({"message": "Failed", "error": serializer.errors}, status=400)

# Category Delete
@permission_classes([IsAdminUser])
@api_view(['DELETE'])
def category_delete(request):
    category_id = request.data.get("id")
    if not category_id:
        return Response({"error": "enter category id please"}, status=400)
    try:
        product = CategoryName.objects.get(id=category_id)
        product.delete()
        return Response({"message": "Category deleted"}, status=200)
    except CategoryName.DoesNotExist:
        return Response({"error": "Category not found"}, status=404)

# Product Create
# @permission_classes([IsAdminUser])
# @api_view(['POST'])
# def product_create(request):
#     serializer = ProductSerializer(data = request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response({"message": "Product added", "product": serializer.data},status=201)
#     return Response({"message": "Failed", "error": serializer.errors}, status=400)

# # Product Get
# @permission_classes([IsAdminUser])
# @api_view(['GET'])
# def product_detail_get(request):
#     data = Product.objects.all()
#     serializer = ProductSerializer(data, many=True)
#     return Response({"message": "Product Fatched", "data": serializer.data}, status=200)

#Product Create
@permission_classes([IsAdminUser])
@api_view(['POST'])
def product_create_and_get(request):
    if request.method == 'GET':
        product_id = request.data.get('id')
        data = Product.objects.get(id = product_id)
        serializer = ProductSerializer(data, many=True)
        return Response({"message": "Fatched", "data": serializer.data}, status=200)
    
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Product added", "data": serializer.data}, status=201)
        return Response({"message": "Failed", "error": serializer.errors}, status=400)


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

