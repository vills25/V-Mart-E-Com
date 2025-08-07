from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from django.db import transaction
from myapp.models import *
from myapp.serializers import *

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