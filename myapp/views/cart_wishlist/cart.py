from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction

from myapp.models import *
from myapp.serializers import *

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
