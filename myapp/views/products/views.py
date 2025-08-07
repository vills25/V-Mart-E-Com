from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from myapp.models import *
from myapp.serializers import *
from django.db.models import Q


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