from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.db import transaction
from myapp.models import *
from myapp.serializers import *

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