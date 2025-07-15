from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from django.db import transaction
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from .serializers import *

# register Seller
@api_view(['POST'])
def register_seller(request):
    required_fields = ['username', 'email', 'password', 'mobile_no', 'address']
    data = request.data
    
    if not all(field in data for field in required_fields):
        return Response({"error": "please fill all fields"}, status=status.HTTP_400_BAD_REQUEST)
  
    try:
        with transaction.atomic():
            # Check if username, email exists
            if User.objects.filter(username=data['username']).exists():
                return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
            
            if User.objects.filter(email=data['email']).exists():
                return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            
            if Seller.objects.filter(mobile_no=data['mobile_no']).exists():
                return Response({"error": "Mobile number already registered"}, status=status.HTTP_400_BAD_REQUEST)

            # Create User
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''))
            
            # Create Seller
            seller = Seller.objects.create(
                user=user,
                profile_picture=data.get('profile_picture'),
                mobile_no=data['mobile_no'],
                address=data['address'],)
            
            return Response({"message": "Seller registered successfully",
                "seller_id": seller.id,
                "username": user.username,
                "email": user.email
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# register Buyer
@api_view(['POST'])
def register_buyer(request):
    required_fields = ['username', 'email', 'password', 'mobile_no', 'address']
    data = request.data
    
    if not all(field in data for field in required_fields):
        return Response({"error": "please fill all fields"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            if User.objects.filter(username=data['username']).exists():
                return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
            
            if User.objects.filter(email=data['email']).exists():
                return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            
            if Buyer.objects.filter(mobile_no=data['mobile_no']).exists():
                return Response({"error": "Mobile number already exists"}, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.create_user(
                                        username=data['username'], email=data['email'],
                                        password=data['password'],
                                        first_name=data.get('first_name', ''),
                                        last_name=data.get('last_name', ''))
            
            buyer = Buyer.objects.create(user=user,
                                         mobile_no=data['mobile_no'],
                                         address=data['address'],
                                         profile_picture=data.get('profile_picture'))
            
            return Response({
                "message": "Buyer registered successfully",
                "buyer_id": buyer.id,
                "username": user.username,
                "email": user.email
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Login Buyer & Seller 
@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    
    if not user:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    
    refresh = RefreshToken.for_user(user)
    
    # Check user type
    try:
        seller = Seller.objects.get(user=user)
        user_type = 'seller'
        user_data = {
            "id": seller.id,
            "username": user.username,
            "email": user.email,
            "mobile_no": seller.mobile_no,
            "is_verified": seller.is_verified
        }
    except Seller.DoesNotExist:
        try:
            buyer = Buyer.objects.get(user=user)
            user_type = 'buyer'
            user_data = {
                "id": buyer.id,
                "username": user.username,
                "email": user.email,
                "mobile_no": buyer.mobile_no
            }
        except Buyer.DoesNotExist:
            return Response({"error": "User type not recognized"}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': user_data,
        'user_type': user_type
    })
