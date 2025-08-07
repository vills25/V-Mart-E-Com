from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from myapp.models import *
from myapp.serializers import *
from datetime import datetime

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

