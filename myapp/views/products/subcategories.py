from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from django.db import transaction
from myapp.models import *
from myapp.serializers import *


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