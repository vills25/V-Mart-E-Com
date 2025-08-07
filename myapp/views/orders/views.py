from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from myapp.models import *
from myapp.serializers import *
import random
from decimal import Decimal

def generate_order_id():
    order_name = "#ord"
    number_generate = random.randint(10000, 99999) 
    return f"{order_name}{number_generate}"

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
