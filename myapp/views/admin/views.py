from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from myapp.models import *
from myapp.serializers import *


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