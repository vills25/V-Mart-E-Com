from datetime import datetime
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import status
from django.db import transaction
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from .serializers import *
from django.db.models import Q
import random
from decimal import Decimal

def generate_order_id():
    order_name = "#ord"
    number_generate = random.randint(10000, 99999) 
    return f"{order_name}{number_generate}"

def valid_email(email):
    if '@' in email and '.' in email:
        return email
    else:
        return False

# register Seller
@api_view(['POST'])
def register_seller(request):
    required_fields = ['username', 'email', 'password', 'mobile_no', 'address']
    data = request.data

    if not all(field in data for field in required_fields):
        return Response({"error": "please fill all fields"}, status=status.HTTP_400_BAD_REQUEST)
      
    check_mobile_no = data['mobile_no']
    if not (check_mobile_no.isdigit() and len(check_mobile_no) == 10):
        return Response({"error": "Invalid mobile number. Please enter 10-digit mobile number."}, status=status.HTTP_400_BAD_REQUEST)

    if not valid_email(data['email']):
        return Response({"error": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST)

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
                "seller_id": seller.seller_id,
                "username": user.username,
                "email": user.email
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Update Seller 
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_seller(request):
    try:
        get_seller_id = request.data.get('seller_id')
        seller = Seller.objects.get(seller_id=get_seller_id)
        user = seller.user
        data = request.data

        with transaction.atomic():

            if 'username' in data:
                if User.objects.filter(username=data['username']).exclude(pk=user.pk).exists():
                    return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)
                user.username = data['username']
            
            if 'email' in data:
                if User.objects.filter(email=data['email']).exclude(pk=user.pk).exists():
                    return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)
                user.email = data['email']
            
            if 'password' in data:
                user.set_password(data['password'])
            
            if 'first_name' in data:
                user.first_name = data['first_name']
            
            if 'last_name' in data:
                user.last_name = data['last_name']
            
            user.save()

            if 'mobile_no' in data:
                if Seller.objects.filter(mobile_no=data['mobile_no']).exclude(pk=seller.pk).exists():
                    return Response({"error": "Mobile number already registered"}, status=status.HTTP_400_BAD_REQUEST)
                seller.mobile_no = data['mobile_no']
            
            if 'address' in data:
                seller.address = data['address']
            
            if 'profile_picture' in data:
                seller.profile_picture = data['profile_picture']
            
            seller.save()

            return Response({
                "message": "Seller updated successfully",
                "seller_id": seller.seller_id,
                "username": user.username,
                "email": user.email
            }, status=status.HTTP_200_OK)

    except Seller.DoesNotExist:
        return Response({"error": "Seller not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Delete Seller 
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def seller_delete(request):
    seller_id = request.data.get('seller_id')
    if not seller_id:
        return Response({"error": "enter Seller id please"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        seller = Seller.objects.get(seller_id = seller_id)
        seller.delete()
        return Response({"message": "Seller deleted"}, status=status.HTTP_200_OK)
    except Buyer.DoesNotExist:
        return Response({"error": "Seller not found"}, status= status.HTTP_404_NOT_FOUND)    

#seller can view his own profile
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def seller_profile_with_products_orders(request):
    try:
        seller = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        return Response({"error": "Seller not found"}, status=status.HTTP_404_NOT_FOUND)

    seller_serializer = SellerSerializer(seller)

    products = Product.objects.filter(seller=seller, is_active=True)
    product_serializer = ProductSerializer(products, many=True)
    
    orders = Order.objects.filter(items__product__seller=seller).distinct()
    order_serializer = OrderDetailSerializer(orders, many=True)
    
    fatched_data = {
        "profile": seller_serializer.data,
        "products": product_serializer.data,
        "orders": order_serializer.data}
    return Response({"Data fatched ":fatched_data}, status=status.HTTP_200_OK)

# ================================================================================================

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
                "buyer_id": buyer.buyer_id,
                "username": user.username,
                "email": user.email
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Update Buyer Profile
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_buyer(request):
    try:

        get_buyer_id = request.data.get('buyer_id')
        buyer = Buyer.objects.get(buyer_id=get_buyer_id)
        user = buyer.user
        data = request.data

        with transaction.atomic():
      
            if 'username' in data:
                if User.objects.filter(username=data['username']).exclude(pk=user.pk).exists():
                    return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)
                user.username = data['username']
            
            if 'email' in data:
                if User.objects.filter(email=data['email']).exclude(pk=user.pk).exists():
                    return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)
                user.email = data['email']
            
            if 'password' in data:
                user.set_password(data['password'])
            
            if 'first_name' in data:
                user.first_name = data['first_name']
            
            if 'last_name' in data:
                user.last_name = data['last_name']
            
            user.save()

            if 'mobile_no' in data:
                if Buyer.objects.filter(mobile_no=data['mobile_no']).exclude(pk=buyer.pk).exists():
                    return Response({"error": "Mobile number already registered"}, status=status.HTTP_400_BAD_REQUEST)
                buyer.mobile_no = data['mobile_no']
            
            if 'address' in data:
                buyer.address = data['address']
            
            if 'profile_picture' in data:
                buyer.profile_picture = data['profile_picture']
            
            buyer.save()

            return Response({
                "message": "Buyer updated successfully",
                "buyer_id": buyer.buyer_id,
                "username": user.username,
                "email": user.email
            }, status=status.HTTP_200_OK)

    except Buyer.DoesNotExist:
        return Response({"error": "Buyer not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)    

#Buyer Delete
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def buyer_delete(request):
    buyer_id = request.data.get('buyer_id')
    if not buyer_id:
        return Response({"error": "enter buyer id please"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        buyer = Buyer.objects.get(buyer_id = buyer_id)
        buyer.delete()
        return Response({"message": "Buyer deleted"}, status=status.HTTP_200_OK)
    except Buyer.DoesNotExist:
        return Response({"error": "Buyer not found"}, status= status.HTTP_404_NOT_FOUND)

# buyer can view his own profile
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buyer_profile_with_orders(request):
    try:
        buyer = Buyer.objects.get(user=request.user)
    except Buyer.DoesNotExist:
        return Response({"error": "Buyer not found"}, status=status.HTTP_404_NOT_FOUND)

    buyer_serializer = BuyerSerializer(buyer)

    orders = Order.objects.filter(buyer=buyer)
    order_serializer = OrderDetailSerializer(orders, many=True)

    fatched_data = {"profile": buyer_serializer.data, "orders": order_serializer.data}
    
    return Response({"Data fatched ":fatched_data}, status=status.HTTP_200_OK)

# ================================================================================================

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
            "seller_id": seller.seller_id,
            "username": user.username,
            "email": user.email,
            "mobile_no": seller.mobile_no,
            "is_verified": seller.is_verified,}
    except Seller.DoesNotExist:

        try:
            buyer = Buyer.objects.get(user=user)
            user_type = 'buyer'
            user_data = {
                "buyer_id": buyer.buyer_id,
                "username": user.username,
                "email": user.email,
                "mobile_no": buyer.mobile_no}
            
        except Buyer.DoesNotExist:
           
            if user.is_staff or user.is_superuser:
                user_type = 'admin'
                user_data = {
                    # "user_id": user.id,
                    "user_id": user.pk,
                    "username": user.username,
                    "email": user.email,
                    "is_superuser": user.is_superuser,
                    "is_staff": user.is_staff
                }
            else:
                return Response({"error": "User type not recognized"}, status=status.HTTP_400_BAD_REQUEST)
        
    return Response({
        'access': str(refresh.access_token),
        'user': user_data,
        'user_type': user_type
    }, status= status.HTTP_201_CREATED)


# Log-Out view
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
    
#Forgot password
@api_view(['POST'])
def forgot_password(request):
    email = request.data.get("email")
    new_password = request.data.get("new_password")
    
    if not email or not new_password:
        return Response({"error": "Enter email and new password please!!"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email__iexact=email)
        user.save()
        return Response({"message": "Password Update Success"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not exist"}, status= status.HTTP_404_NOT_FOUND)

# ================================================================================================

# view all buyers admin only
@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_all_buyers(request):
    try:  
        buyers = Buyer.objects.all().order_by('-created_at')
        serializer = BuyerSerializer(buyers, many=True)
        return Response({"Data fatched ":serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#view all seller admin only
@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_all_sellers(request):
    try:
        sellers = Seller.objects.all().order_by('-created_at')
        serializer = SellerSerializer(sellers, many=True)
        return Response({"Data fatched ":serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST) 

# ================================================================================================

# Category show/get 
@api_view(['GET'])
def category_get(request, pk=None):
    try:
        if pk:
            # Get single category by ID
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category)
            return Response({"category": serializer.data}, status=status.HTTP_200_OK)
        else:
            # Get all categories if no ID 
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            return Response({"categories": serializer.data}, status=status.HTTP_200_OK)
        
    except Category.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# category create/add
@api_view(['POST'])
@permission_classes([IsAdminUser])
def category_create(request):
    data = request.data

    if 'category_name' not in data:
        return Response({"error":"categoryname is required"}, status= status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            category = Category.objects.create(
                category_name = data['category_name'],
                category_detail = data.get('category_detail', ''),  
                created_by = request.user,  
                updated_by = request.user  
            ) 
            return Response({
                "message": "category created successfull",
                "category":{
                    'category_id': category.category_id,
                    'category_name': category.category_name,
                    'category_detail': category.category_detail,
                }
            }, status= status.HTTP_201_CREATED)

    except Exception as e :
        return Response({"error":str(e)}, status= status.HTTP_400_BAD_REQUEST)


# category category update/change
@api_view(['PUT'])
@permission_classes([IsAdminUser, IsAuthenticated])
def category_update(request, pk):
    try:
        category = Category.objects.get(pk =pk) 
    except Category.DoesNotExist:
        return Response({"Error": "Category not founnd"}, status= status.HTTP_404_NOT_FOUND)
    data = request.data
    if not data.get('category_name'):
        return Response({"Error": "category_name is required"})

    try:
        category.category_name = data['category_name']
        category.category_detail = data['category_detail']
        category.save()
        return Response({"Category Updated": category},status= status.HTTP_205_RESET_CONTENT)
    except Exception as e :
        return Response({"error": str(e)}, status = status.HTTP_400_BAD_REQUEST)

# category remove/delete
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def category_delete(request, pk):
    try:
        category = Category.objects.get(pk =pk )
    except Category.DoesNotExist:
        return Response({"error": "Category not found"}, status= status.HTTP_404_NOT_FOUND)
    try:
        category.delete()
        return Response({"Category Deleted"}, status= status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)        
    
# ================================================================================================

# Sub Category show/get 
@api_view(['GET'])
def subcategory_get(request, pk=None):
    try:
        if pk:

            subcategory = SubCategory.objects.get(pk=pk)
            serializer = SubCategorySerializer(subcategory)
            return Response({"subcategory": serializer.data}, status=status.HTTP_200_OK)
        else:

            category_id = request.GET.get('category_id')
            if category_id:
                subcategories = SubCategory.objects.filter(category=category_id)
            else:
                subcategories = SubCategory.objects.all()
                
            serializer = SubCategorySerializer(subcategories, many=True)
            return Response({"subcategories": serializer.data}, status=status.HTTP_200_OK)
        
    except SubCategory.DoesNotExist:
        return Response({"error": "Subcategory not found"}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Sub category create/add
@api_view(['POST'])
@permission_classes([IsAdminUser])
def subcategory_create(request):
    data = request.data
    
    if 'subcategory_name' not in data or 'category' not in data:
        return Response({"error":"subcategoryname and category id is required"}, status= status.HTTP_400_BAD_REQUEST)
    
    try:
         with transaction.atomic():
            # Check if category exists
            category = Category.objects.get(pk=data['category'])
            
            subcategory = SubCategory.objects.create(
                subcategory_name=data['subcategory_name'],
                subcategory_detail=data.get('subcategory_detail', ''),
                category=category,
                created_by = request.user,  
                updated_by = request.user
            )
            
            return Response({
                "message": "Subcategory created successfully",
                "subcategory": {
                    'subcategory_id': subcategory.subcategory_id,
                    'subcategory_name': subcategory.subcategory_name,
                    'subcategory_detail': subcategory.subcategory_detail,
                    'category': {
                        'category_id': category.category_id,
                        'category_name': category.category_name
                    }
                }
            }, status=status.HTTP_201_CREATED)
    except Category.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Sub category remove/delete
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def subcategory_delete(request, pk):
    try:
        subcategory = SubCategory.objects.get(pk=pk)
    except SubCategory.DoesNotExist:
        return Response({"error": "Subcategory not found"}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        subcategory.delete()
        return Response({"message": "Subcategory deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Sub category category update/change
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def subcategory_update(request):
    data = request.data
  
    if 'subcategory_id' not in data:
        return Response({"error": "subcategory_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # check for subcategory_id
    try:
        subcategory = SubCategory.objects.get(pk=data['subcategory_id'])
    except SubCategory.DoesNotExist:
        return Response({"error": "Subcategory not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Validate required fields
    if 'subcategory_name' not in data or 'category' not in data:
        return Response({"error": " subcategory_name and category is required"}, status=status.HTTP_400_BAD_REQUEST)
     
    try:
        category = Category.objects.get(pk=data['category'])
        
        subcategory.subcategory_name = data['subcategory_name']
        if 'subcategory_detail' in data:
            subcategory.subcategory_detail = data['subcategory_detail']
        subcategory.category = category
        subcategory.save()
        
        return Response({
            "message": "Subcategory updated successfully",
            "subcategory": {
                'subcategory_id': subcategory.subcategory_id,
                'subcategory_name': subcategory.subcategory_name,
                'subcategory_detail': subcategory.subcategory_detail,
                'category': {
                    'category_id': category.category_id,
                    'category_name': category.category_name
                }
            }
        })
    except Category.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ================================================================================================

# Show Product by id or get all product
@api_view(['GET'])
def product_get(request):
    product_id = request.data.get('product_id') 

    if product_id:
        try:
            product = Product.objects.get(pk=product_id, is_active=True)
            serializer = ProductSerializer(product)
            return Response({"Product data": serializer.data}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    else:
        all_products = Product.objects.filter(is_active=True)
        serializer = ProductSerializer(all_products, many=True)
        return Response({"all_products": serializer.data}, status=status.HTTP_200_OK)
        

# Product Search by category, subcategory, produt name
@api_view(['POST'])
def product_search(request):
    try:
        data = request.data

        product_id = data.get('product_id')
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        category = data.get('category', '').strip()
        sub_category = data.get('sub_category', '').strip()
        price = data.get('price')
        brand = data.get('brand', '').strip()
        seller_username = data.get('seller', '').strip()
        tags = data.get('tags', '').strip()
        color = data.get('color', '').strip()
        size = data.get('size', '').strip()
        fabric = data.get('fabric', '').strip()
        sort_by = data.get('sort_by', '').strip().lower()
        
        queryset = Product.objects.filter(is_active=True)

        if product_id:
            queryset = queryset.filter(pk=product_id)

        if name:
            queryset = queryset.filter(name__icontains=name)

        if description:
            queryset = queryset.filter(description__icontains=description)

        if category:
            try:
                queryset = queryset.filter(category__category_name__icontains=category)
            except:
                queryset = queryset.filter(category__icontains=category)

        if sub_category:
            try:
                queryset = queryset.filter(sub_category__sub_category_name__icontains=sub_category)
            except:
                queryset = queryset.filter(sub_category__icontains=sub_category)

        if price:
            try:
                price = float(price)
                queryset = queryset.filter(Q(price=price) | Q(sale_price=price))
            except ValueError:
                return Response({"error": "Invalid price format"}, status=status.HTTP_400_BAD_REQUEST)

        if brand:
            queryset = queryset.filter(brand__icontains=brand)

        if seller_username:
            queryset = queryset.filter(seller__user__username__icontains=seller_username)

        if tags:
            queryset = queryset.filter(tags__icontains=tags)

        if color:
            queryset = queryset.filter(color__icontains=color)

        if size:
            queryset = queryset.filter(size__icontains=size)

        if fabric:
            queryset = queryset.filter(fabric__icontains=fabric)    
        
        sort_options = {
            'price_low': 'price',
            'price_high': '-price',
            'newest': '-created_at',

        }

        if sort_by in sort_options:
            try:
                queryset = queryset.order_by(sort_options[sort_by])
            except:
                return Response({"error": "Invalid sort field"}, status=status.HTTP_400_BAD_REQUEST)

        if not queryset.exists():
            return Response({"message": "No matching products found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(queryset, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# PRODUCT CREATE
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def product_create(request):

    try:
        seller_username = request.data.get('seller')
        get_seller = Seller.objects.get(user__username=seller_username)
    except Seller.DoesNotExist:
        return Response({"error": "Invalid  or seller not exist"}, status= status.HTTP_400_BAD_REQUEST)


    required_fields = ['name', 'description', 'price', 'quantity', 'category', 'sub_category', 'brand']
    data = request.data

    if not all(field in data for field in required_fields):
        return Response({"Please fill all required  fields"}, status= status.HTTP_400_BAD_REQUEST)
    
    price = float(data['price'])
    if price < 0 :
        return Response({"Price should be greater then Zero"}, status= status.HTTP_400_BAD_REQUEST)
    
    sale_price = float(data['sale_price'])
    if sale_price >= price:
        return Response({"Sale price should be less than actual price"}, status= status.HTTP_400_BAD_REQUEST)

    quantity = data['quantity']
    if quantity <= 0:
        return Response({"Product quantity should be greater than zero"}, status= status.HTTP_400_BAD_REQUEST)

    try:
        category_instance = Category.objects.get(pk=data['category'])
        subcategory_instance = SubCategory.objects.get(pk=data['sub_category'])
    except (Category.DoesNotExist, SubCategory.DoesNotExist):
        return Response({"error": "Invalid category or subcategory"}, status= status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():    
            create_product = Product.objects.create(
                seller = get_seller,
                name=data['name'],
                description=data['description'],
                price=price,
                sale_price=sale_price,
                quantity=quantity,
                category=category_instance,
                sub_category=subcategory_instance,
                brand=data['brand'],
                tags=data.get('tags', ''),
                size=data.get('size', ''),
                color=data.get('color', ''),
                fabric=data.get('fabric', ''),
                in_stock=quantity > 0,
                created_by = request.user
            )
            serializer = ProductSerializer(create_product)
            return Response({"Message": "Product created successfully", "Product data": serializer.data}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Product Update
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def product_update(request):

    try:
        seller = Seller.objects.get(user=request.user)
        product_id = request.data.get('product_id') 
        if not product_id:
            return Response({"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        product = Product.objects.get(pk=product_id, seller=seller)
    except Seller.DoesNotExist:
        return Response({"error": "Only sellers can update products"}, status=status.HTTP_403_FORBIDDEN)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND) 

    data = request.data
    
    try:
        category_instance = Category.objects.get(pk=data['category'])
        subcategory_instance = SubCategory.objects.get(pk=data['sub_category'])
    except (Category.DoesNotExist, SubCategory.DoesNotExist):
        return Response({"error": "Invalid category and subcategory or Not exists."}, status=400)

    try:

        if 'name' in data:
            product.name = data['name']

        if 'description' in data:
            product.description = data['description']

        if 'price' in data:
            if data['price'] < 0:
              return Response({"Price should be greater then Zero"}, status=status.HTTP_400_BAD_REQUEST)
            product.price = data['price'] 

        if 'sale_price' in data:
            if data['sale_price'] > product.price:
              return Response({"sale Price should be less then actual product"}, status=status.HTTP_400_BAD_REQUEST)
            product.price = data['sale_price']
            
        if 'quantity' in data:
            if data['quantity'] < 0:
              return Response({"quantity should be greater then Zero"}, status=status.HTTP_400_BAD_REQUEST)
            product.price = data['quantity']

        if 'category' in data:
            product.category = category_instance   

        if 'sub_category' in data:
            product.sub_category = subcategory_instance

        if 'brand' in data:
            product.brand = data['brand']

        if 'tags' in data:
            product.tags =  data['tags']

        if 'size' in data:
            product.size = data['size']

        if 'color'in data:
            product.color = data['color']

        if 'fabric'in data:
            product.fabric = data['fabric']
        
        updated_by = request.user
        product.save()
        serializer = ProductSerializer(product)
        return Response ({"Message":"Product Updated", 'seller': seller.seller_id, "updated product data": serializer.data}, status= status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
# Product Delete 
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def product_delete(request):
    try:
        seller = Seller.objects.get(user=request.user)
        product_id = request.data.get('product_id') 
        if not product_id:
            return Response({"error": "product_id is required to delete Product"}, status=status.HTTP_400_BAD_REQUEST)
        
        product = Product.objects.get(pk=product_id, seller=seller)
        product.delete()
        return Response({"Product Deleted"}, status=status.HTTP_200_OK)
    except Seller.DoesNotExist:
        return Response({"error": "Only sellers can Delete products"}, status=status.HTTP_403_FORBIDDEN)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
  
# ================================================================================================

# CART Implement

# Cart Get
@api_view(['GET'])
def cart_get(request):

    try:
        cart_id = request.data.get('cart_id') 
        if not cart_id:
            return Response({"Please enter Cart ID"}, status= status.HTTP_400_BAD_REQUEST)

        get_cart = Cart.objects.get(pk = cart_id, buyer__user = request.user)
        get_items = CartItem.objects.filter(cart=get_cart).select_related('product')
        
        total_items = get_items.count()
        subtotal = sum(
            item.quantity * (item.product.sale_price if item.product.sale_price else item.product.price)
            for item in get_items
        )
        
        serializer = CartItemSerializer(get_items, many=True)
        return Response({
            "cart_id": get_cart.cart_id,
            "total_items": total_items,
            "subtotal": subtotal,
            "items": serializer.data
        })
        
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
   

# Cart Create
@api_view(['POST'])
def cart_create(request):
    buyer_id = request.data.get('buyer_id')
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity')

    if not all([buyer_id, product_id, quantity]):
        return Response({"error": "buyer_id, product_id, and quantity are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        buyer = Buyer.objects.get(buyer_id=buyer_id)
    except Buyer.DoesNotExist:
        return Response({"error": "Buyer not found"}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        product = Product.objects.get(pk=product_id, is_active=True, in_stock=True)
    except Product.DoesNotExist:
        return Response({"error": "Product not available"}, status=status.HTTP_404_NOT_FOUND)

    cart, _ = Cart.objects.get_or_create(buyer=buyer)

    quantity = int(quantity)
    if quantity < 1:
        return Response({"error": "Quantity must be at least 1"}, status=status.HTTP_400_BAD_REQUEST)

    existing_item = CartItem.objects.filter(
        cart=cart,
        product=product,
        selected_color=request.data.get('color', ''),
        selected_size=request.data.get('size', '')
    ).first()

    if existing_item:
        existing_item.quantity += quantity
        existing_item.save()
        action = "Quantity updated"
    else:
        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=quantity,
            selected_color=request.data.get('color', ''),
            selected_size=request.data.get('size', '')
        )
        action = "Item added"

    return Response({
        "message": f"{action} successfully",
        "cart_id": cart.cart_id,
        "buyer_id": buyer.buyer_id
    }, status=status.HTTP_201_CREATED)


# Cart Items Update
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def cart_items_update(request):
    try:
        cart_item_id = request.data.get('cart_item_id')
        if not cart_item_id:
            return Response({'error': 'cart_item_id required'},status= status.HTTP_400_BAD_REQUEST)
        try:
            cart_item = CartItem.objects.get(id=cart_item_id)
            cart_item.quantity = request.data.get('quantity', cart_item.quantity)
            cart_item.save()
            return Response({'message': 'Cart Item updated', "item_id": cart_item, "new_quantity": cart_item.quantity},status= status.HTTP_201_CREATED)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status= status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Cart Delete
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cart_delete(request):
    try:
        buyer = Buyer.objects.get(user=request.user)
        cart_id = request.data.get('cart_id') 
        if not cart_id:
            return Response({"error": "cart_id is required to delete Product"}, status=status.HTTP_400_BAD_REQUEST)
        
        cart = Cart.objects.get(pk=cart_id, buyer=buyer)
        cart.delete()
        return Response({"Cart Deleted"}, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

# =======================================================================================================================================

# Order Create
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    try:
        get_buyer_id = Buyer.objects.get(user=request.data['buyer_id'])
    except Buyer.DoesNotExist:
        return Response({"error": "Buyer not exist or invalid buyer id"}, status=status.HTTP_403_FORBIDDEN)
    
    data = request.data
    
    required_fields = ['payment_method', 'transaction_id', 'delivery_address', 'delivery_contact']
    if not all(field in data for field in required_fields):
        return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
    
    if len(data['delivery_address']) <= 20:
        return Response({"error": "Please enter your full delivery address including house/flat no., Street name, Area, landmark, Pincode, City and State"}, 
                       status=status.HTTP_400_BAD_REQUEST)

    if len(data['delivery_contact']) < 10:
        return Response({"error": "Please enter a valid 10-digit mobile number"}, status=status.HTTP_400_BAD_REQUEST)
                       

    try:
        with transaction.atomic():
            try:
                cart = Cart.objects.get(buyer=get_buyer_id)
                cart_items = CartItem.objects.filter(cart=cart).select_related('product')
            except Cart.DoesNotExist:
                return Response({"error": "No cart found for this buyer"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not cart_items.exists():
                return Response({"error": "Your cart is empty. Add products to cart before placing order"}, status=status.HTTP_400_BAD_REQUEST)
                              
            
            # Check all products are available
            for item in cart_items:
                if not item.product.is_active or not item.product.in_stock:
                    return Response({"error": f"Product {item.product.name} is not available"}, status=status.HTTP_400_BAD_REQUEST)
                                  
                if item.quantity > item.product.quantity:
                    return Response({"error": f"Not enough stock for product {item.product.name}"}, status=status.HTTP_400_BAD_REQUEST)
                                  
            # cod status
            payment_status = 'COD' if data['payment_method'].upper() == 'COD' else 'COMPLETED'
            order_status = 'COD' if data['payment_method'].upper() == 'COD' else 'PENDING'

            # Create payment
            payment = Payment.objects.create(
                buyer=get_buyer_id,
                amount=0,
                payment_method=data['payment_method'],
                transaction_id=data['transaction_id'],
                status=payment_status
            )
            
            # Create order
            order = Order.objects.create(
                buyer=get_buyer_id,
                payment=payment,
                order_number=generate_order_id(),
                status=order_status,
                total=0
            )
            
            total_amount = 0
            order_items = []
            
            # Process each cart item
            for cart_item in cart_items:
                product = cart_item.product
                quantity = cart_item.quantity
                price = product.sale_price if product.sale_price else product.price
                item_total = price * quantity

                # Create order item
                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price,
                    color=cart_item.selected_color,
                    size=cart_item.selected_size,
                    delivery_contact=data['delivery_contact'],
                    delivery_address=data['delivery_address']              
                )

                # Update product quantity
                product.quantity -= quantity
                product.in_stock = product.quantity > 0
                product.save()
                
                total_amount += item_total
                order_items.append({
                    "product_id": product.product_id,
                    "name": product.name,
                    "quantity": quantity,
                    "price": str(price),
                    "item_total": str(item_total),
                })
            
            # Update payment and order with total amount
            payment.amount = Decimal(str(total_amount))
            payment.save()
            
            order.total = Decimal(str(total_amount))
            order.save()
            
            # Clear the cart after successful order placement
            cart_items.delete()
            cart.delete()

            return Response({
                "message": "Your Order has been Placed successfully",
                "order_number": order.order_number,
                "status": order.status,
                "total": str(total_amount),
                "delivery_address": data['delivery_address'],
                "delivery_contact": data['delivery_contact'],
                "items": order_items
            }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Order view for Buyer
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_list(request):
    try:
        buyer = Buyer.objects.get(user=request.user)
    except Buyer.DoesNotExist:
        return Response({"error": "Only buyers can view orders"}, status=status.HTTP_403_FORBIDDEN)
    
    status_filter = request.GET.get('status')
    orders = Order.objects.filter(buyer=buyer).order_by('-order_date')

    if status_filter:
        status_filter = status_filter.upper()
        orders = orders.filter(status=status_filter)

    if not orders.exists():
        return Response({"message": "No orders found for this buyer or filter"}, status=status.HTTP_200_OK)

    serializer = OrderSerializer(orders, many=True)
    return Response({"order data": serializer.data}, status=status.HTTP_200_OK)
 
# Seller can see his Orders details
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def seller_order_list(request):
    try:
        seller = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        return Response({"error": "Only sellers can view these orders"}, status=status.HTTP_403_FORBIDDEN)
    
    status_filter = request.GET.get('status')
    
    orders = Order.objects.filter(items__product__seller=seller).distinct().order_by('-order_date')
    
    if status_filter:
        orders = orders.filter(status=status_filter.upper())
   
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

# Update Order Details By seller 
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_order_status(request):
    try:
        seller = Seller.objects.get(user=request.user)
        order_number = request.data.get('order_number')
  
        if not order_number:
            return Response({"error": "order_number is required"}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.get(order_number=order_number)
        
        # Ensure the seller is part of the order
        if not OrderItem.objects.filter(order=order, product__seller=seller).exists():
            return Response({"error": "You can only update orders of your products"}, status=status.HTTP_403_FORBIDDEN)

    except Seller.DoesNotExist:
        return Response({"error": "Only sellers can update order status"}, status=status.HTTP_403_FORBIDDEN)

    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    tracking_number = request.data.get('tracking_number', '')
    shipping_company = request.data.get('shipping_company', '')
    notes = request.data.get('notes', '')

    if not new_status:
        return Response({"error": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)

    valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
    if new_status.upper() not in valid_statuses:
        return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

    # Update fields
    order.status = new_status.upper()
    order.tracking_number = tracking_number
    order.shipping_company = shipping_company
    order.notes = notes

    if new_status.upper() == 'SHIPPED' and not order.dispatch_date:
        order.dispatch_date = datetime.now()
    elif new_status.upper() == 'DELIVERED' and not order.delivery_date:
        order.delivery_date = datetime.now()

    order.save()

    return Response({
        "message": "Order status updated successfully.",
        "order_number": order.order_number,
        "new_status": order.status,
        "tracking_number": order.tracking_number,
        "shipping_company": order.shipping_company
    }, status=status.HTTP_200_OK)

# =======================================================================================================================================

# Product Review Create
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request):
    try:
        buyer = Buyer.objects.get(user=request.user)
    except Buyer.DoesNotExist:
        return Response({"error": "Buyer does not exist"}, status=status.HTTP_403_FORBIDDEN)

    data = request.data
    product_id = data.get('product_id')

    if not product_id:
        return Response({"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(product_id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        rating = int(data.get('rating', 0))
        if rating < 1 or rating > 5:
            return Response({"error": "Please rate between 1 and 5"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if already reviewed
        if ProductReview.objects.filter(product=product, buyer=buyer).exists():
            return Response({"error": "You have already reviewed this product"}, status=status.HTTP_400_BAD_REQUEST)

        # Check purchase
        if_purchased = OrderItem.objects.filter(
                product=product,
                order__buyer=buyer,
                order__status='DELIVERED'
            ).exists()

        if not if_purchased:
            return Response({"error": "You can only review products you've purchased"}, status=status.HTTP_403_FORBIDDEN)

        # Create review
        review = ProductReview.objects.create(
            product=product,
            buyer=buyer,
            rating=rating,
            comment=data.get('comment', '')
        )

        return Response({
            "message": "Review submitted successfully",
            "review_id": review.product_review_id,
            "product_id": product.product_id,
            "rating": review.rating
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Review Update
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_review(request):
    try:
        buyer = Buyer.objects.get(user=request.user)
    except Buyer.DoesNotExist:
        return Response({"error": "Buyer does not exist"}, status=status.HTTP_403_FORBIDDEN)

    try:
        review_id = request.data.get('review_id')
        review = ProductReview.objects.get(product_review_id=review_id, buyer=buyer)
    except ProductReview.DoesNotExist:
        return Response({"error": "Review not founs"}, status=status.HTTP_404_NOT_FOUND)

    data = request.data

    try:
        if 'rating' in data:
            rating = int(data['rating'])
            if rating < 1 or rating > 5:
                return Response({"error": "Please rate between 1 and 5"}, status=status.HTTP_400_BAD_REQUEST)
            review.rating = rating

        if 'comment' in data:
            review.comment = data['comment']

        review.save()

        return Response({
            "message": "Review updated successfully",
            "review_id": review.product_review_id,
            "product_id": review.product.product_id,
            "rating": review.rating,
            "comment": review.comment
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Review Delete
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request):

    get_review_id = request.data.get('product_review_id')

    if not get_review_id:
        return Response({'error': 'review_id required'},status= status.HTTP_400_BAD_REQUEST)
    try:
        ProductReview.objects.get(product_review_id=get_review_id).delete()
        return Response({'message': 'Review deleted'}, status=status.HTTP_200_OK)
    
    except ProductReview.DoesNotExist:
        return Response({'error': 'Review not found'},status= status.HTTP_404_NOT_FOUND)

# =======================================================================================================================================

#Wishlist Add product
@api_view(['POST'])
@permission_classes([AllowAny])
def wishlist_create(request):
    try:
        buyer = Buyer.objects.get(user=request.data['buyer_id'])
        product = Product.objects.get(product_id=request.data['product_id'])

        with transaction.atomic():
            Wishlist.objects.create(
                buyer=buyer,
                product=product,
                added_by=buyer
            )
            return Response({"Product Added To Wishlist"}, status=status.HTTP_201_CREATED) 
    
    except Buyer.DoesNotExist:
        return Response({"error": "Buyer does not exist"}, status=status.HTTP_403_FORBIDDEN)
    
    except Product.DoesNotExist:
        return Response({"error": "Entered product does not exist"}, status=status.HTTP_403_FORBIDDEN)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Wishlist remove Item
@api_view(['DELETE'])
@permission_classes([AllowAny])
def wishlist_remove(request):
    wishlist_id = request.data.get('wishlist_id')
    if not wishlist_id:
        return Response({'error': 'wishlist_id required'},status= status.HTTP_400_BAD_REQUEST)
    try:
        Wishlist.objects.get(wishlist_id=wishlist_id).delete()
        return Response({'message': 'Wishlist item deleted'}, status=status.HTTP_200_OK)
    
    except Wishlist.DoesNotExist:
        return Response({'error': 'Wishlist item not found'},status= status.HTTP_404_NOT_FOUND)

# =======================================================================================================================================

# cancel order and payment refund process
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def cancel_order_and_refund(request):
    try:
        get_buyer = request.data.get('buyer_id')
    except Buyer.DoesNotExist:
        return Response({"error": "Buyer Not Exist or invalid buyer"}, status=status.HTTP_403_FORBIDDEN)

    order_number = request.data.get('order_number')
    cancel_reason = request.data.get('cancel_reason', '')

    if not order_number or not cancel_reason:
        return Response({"error": "order_number and cancel_reason required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        order = Order.objects.get(order_number=order_number, buyer=get_buyer)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    if order.status not in ['PENDING', 'COD','SHIPPED' ,'DELIVERED', 'PROCESSING']:
        return Response({"error": f"Cannot cancel order with status {order.status}"}, status=status.HTTP_400_BAD_REQUEST)

    order.status = 'CANCELLED'

    if order.status == 'DELIVERED' or (order.payment and order.payment.payment_method and order.payment.payment_method.upper() != 'COD'): # cgeck if ordder.payment is not none before using payment_method
        order.refund_status = 'REQUESTED'

    order.refund_reason = cancel_reason
    order.refund_date = datetime.now()
    order.save()

    # Restore product stock
    for item in OrderItem.objects.filter(order=order):
        product = item.product
        product.quantity += item.quantity
        product.in_stock = True
        product.save()

    return Response({
        "message": "Order cancelled successfully",
        "order_number": order.order_number,
        "status": order.status,
        "refund_status": order.refund_status,
        "refund_reason": order.refund_reason
    }, status=status.HTTP_200_OK)


# Update refund Status By Seller
@api_view(['PUT'])
@permission_classes([IsAuthenticated]) 
def update_refund_status(request):
    
    try:
        seller = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        return Response({"error": "Only sellers can update refund status"}, status=status.HTTP_403_FORBIDDEN)

    order_number = request.data.get('order_number')
    refund_status = request.data.get('refund_status')
    refund_response = request.data.get('refund_response', '')
    
    if not order_number or not refund_status:
        return Response({"error": "order_number and refund_status are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate refund status values
    # valid_statuses = ['REQUESTED', 'APPROVED', 'REJECTED', 'PROCESSED']
    valid_status = Order.REFUND_STATUS_CHOICES

    if refund_status not in valid_status:
        return Response({"error": "Invalid status"},status=status.HTTP_400_BAD_REQUEST)
    
    try:
        order = Order.objects.get(order_number=order_number)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    if order.status != 'CANCELLED':
        return Response({"error": "Only cancelled orders can have refund status updated"},status=status.HTTP_400_BAD_REQUEST)

    order.refund_status = refund_status
    order.refund_response = refund_response
    
    if refund_status == 'PROCESSED':
        order.refund_date = datetime.now()
        if order.payment:
            order.payment.refund_amount = order.total
            order.payment.refund_date = datetime.now()
            order.payment.status = 'REFUNDED'
            order.payment.save()
    
    order.save()
    
    return Response({
        "message": "Refund status updated successfully",
        "order_number": order.order_number,
        "refund_status": order.refund_status,
        "refund_response": order.refund_response,
        "refund_date": order.refund_date
    }, status=status.HTTP_200_OK)