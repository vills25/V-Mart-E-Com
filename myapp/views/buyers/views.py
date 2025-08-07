from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from myapp.models import *
from myapp.serializers import *


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