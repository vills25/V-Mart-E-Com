from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import status
from django.db import transaction
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from .serializers import *

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
                    "user_id": user.id, # type: ignore
                    "username": user.username,
                    "email": user.email,
                    "is_superuser": user.is_superuser,
                    "is_staff": user.is_staff
                }
            else:
                return Response({"error": "User type not recognized"}, status=status.HTTP_400_BAD_REQUEST)
        
    return Response({
        'refresh': str(refresh),
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

#-----------------------------------------------------------------------------------------------------------------------------------------

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

# buyer can view his own profile
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buyer_profile_with_orders(request):
    try:
        buyer = Buyer.objects.get(user=request.user)
    except Buyer.DoesNotExist:
        return Response({"error": "Buyer not found"}, status=status.HTTP_404_NOT_FOUND)

    # Get buyer profile
    buyer_serializer = BuyerSerializer(buyer)
    
    # Get all orders for this buyer with order items
    orders = Order.objects.filter(buyer=buyer)
    order_serializer = OrderDetailSerializer(orders, many=True)

    fatched_data = {"profile": buyer_serializer.data, "orders": order_serializer.data}
    
    return Response({"Data fatched ":fatched_data}, status=status.HTTP_200_OK)

#seller can view his own profile
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def seller_profile_with_products_orders(request):
    try:
        seller = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        return Response({"error": "Seller not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Get seller profile
    seller_serializer = SellerSerializer(seller)
    
    # Get all products for this seller
    products = Product.objects.filter(seller=seller, is_active=True)
    product_serializer = ProductSerializer(products, many=True)
    
    # Get all orders including seller's products
    orders = Order.objects.filter(items__product__seller=seller).distinct()
    order_serializer = OrderDetailSerializer(orders, many=True)
    
    fatched_data = {
        "profile": seller_serializer.data,
        "products": product_serializer.data,
        "orders": order_serializer.data}
    return Response({"Data fatched ":fatched_data}, status=status.HTTP_200_OK)

#----------------------------------------------------------------------------------------------------------------------------------------

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
    
#----------------------------------------------------------------------------------------------------------------------------------------

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

#----------------------------------------------------------------------------------------------------------------------------------------

# Product get
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
    
    #accept data from user
    data = request.data
    
    #instance for category-subcategory
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
  
#-------------------------------------------------------------------------------------------------
