from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from myapp.models import *
from myapp.serializers import *
from datetime import datetime

# cancel order and payment refund process
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def cancel_order_and_refund(request):
    try:
        get_buyer = request.data.get('buyer_id')
    except Buyer.DoesNotExist:
        return Response({"error": "Buyer Not Exist or invalid buyer"}, status=status.HTTP_403_FORBIDDEN)

    order_number = request.data.get('order_number')
    cancel_reason = request.data.get('cancel_reason', '')

    if not order_number or not cancel_reason:
        return Response({"error": "order_number and cancel_reason required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        order = Order.objects.get(order_number=order_number, buyer=get_buyer)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    if order.status not in ['PENDING', 'COD','SHIPPED' ,'DELIVERED', 'PROCESSING']:
        return Response({"error": f"Cannot cancel order with status {order.status}"}, status=status.HTTP_400_BAD_REQUEST)

    order.status = 'CANCELLED'

    if order.status == 'DELIVERED' or (order.payment and order.payment.payment_method and order.payment.payment_method.upper() != 'COD'): # cgeck if ordder.payment is not none before using payment_method
        order.refund_status = 'REQUESTED'

    order.refund_reason = cancel_reason
    order.refund_date = datetime.now()
    order.save()

    # Restore product stock
    for item in OrderItem.objects.filter(order=order):
        product = item.product
        product.quantity += item.quantity
        product.in_stock = True
        product.save()

    return Response({
        "message": "Order cancelled successfully",
        "order_number": order.order_number,
        "status": order.status,
        "refund_status": order.refund_status,
        "refund_reason": order.refund_reason
    }, status=status.HTTP_200_OK)


# Update refund Status By Seller
@api_view(['PUT'])
@permission_classes([IsAuthenticated]) 
def update_refund_status(request):
    
    try:
        seller = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        return Response({"error": "Only sellers can update refund status"}, status=status.HTTP_403_FORBIDDEN)

    order_number = request.data.get('order_number')
    refund_status = request.data.get('refund_status')
    refund_response = request.data.get('refund_response', '')
    
    if not order_number or not refund_status:
        return Response({"error": "order_number and refund_status are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate refund status values
    # valid_statuses = ['REQUESTED', 'APPROVED', 'REJECTED', 'PROCESSED']
    valid_status = Order.REFUND_STATUS_CHOICES

    if refund_status not in valid_status:
        return Response({"error": "Invalid status"},status=status.HTTP_400_BAD_REQUEST)
    
    try:
        order = Order.objects.get(order_number=order_number)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    if order.status != 'CANCELLED':
        return Response({"error": "Only cancelled orders can have refund status updated"},status=status.HTTP_400_BAD_REQUEST)

    order.refund_status = refund_status
    order.refund_response = refund_response
    
    if refund_status == 'PROCESSED':
        order.refund_date = datetime.now()
        if order.payment:
            order.payment.refund_amount = order.total
            order.payment.refund_date = datetime.now()
            order.payment.status = 'REFUNDED'
            order.payment.save()
    
    order.save()
    
    return Response({
        "message": "Refund status updated successfully",
        "order_number": order.order_number,
        "refund_status": order.refund_status,
        "refund_response": order.refund_response,
        "refund_date": order.refund_date
    }, status=status.HTTP_200_OK)