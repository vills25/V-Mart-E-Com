from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from myapp.models import *
from myapp.serializers import *

# Product Review Create
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request):
    try:
        buyer = Buyer.objects.get(user=request.user)
    except Buyer.DoesNotExist:
        return Response({"error": "Buyer does not exist"}, status=status.HTTP_403_FORBIDDEN)

    data = request.data
    product_id = data.get('product_id')

    if not product_id:
        return Response({"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(product_id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        rating = int(data.get('rating', 0))
        if rating < 1 or rating > 5:
            return Response({"error": "Please rate between 1 and 5"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if already reviewed
        if ProductReview.objects.filter(product=product, buyer=buyer).exists():
            return Response({"error": "You have already reviewed this product"}, status=status.HTTP_400_BAD_REQUEST)

        # Check purchase
        if_purchased = OrderItem.objects.filter(
                product=product,
                order__buyer=buyer,
                order__status='DELIVERED'
            ).exists()

        if not if_purchased:
            return Response({"error": "You can only review products you've purchased"}, status=status.HTTP_403_FORBIDDEN)

        # Create review
        review = ProductReview.objects.create(
            product=product,
            buyer=buyer,
            rating=rating,
            comment=data.get('comment', '')
        )

        return Response({
            "message": "Review submitted successfully",
            "review_id": review.product_review_id,
            "product_id": product.product_id,
            "rating": review.rating
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Review Update
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_review(request):
    try:
        buyer = Buyer.objects.get(user=request.user)
    except Buyer.DoesNotExist:
        return Response({"error": "Buyer does not exist"}, status=status.HTTP_403_FORBIDDEN)

    try:
        review_id = request.data.get('review_id')
        review = ProductReview.objects.get(product_review_id=review_id, buyer=buyer)
    except ProductReview.DoesNotExist:
        return Response({"error": "Review not founs"}, status=status.HTTP_404_NOT_FOUND)

    data = request.data

    try:
        if 'rating' in data:
            rating = int(data['rating'])
            if rating < 1 or rating > 5:
                return Response({"error": "Please rate between 1 and 5"}, status=status.HTTP_400_BAD_REQUEST)
            review.rating = rating

        if 'comment' in data:
            review.comment = data['comment']

        review.save()

        return Response({
            "message": "Review updated successfully",
            "review_id": review.product_review_id,
            "product_id": review.product.product_id,
            "rating": review.rating,
            "comment": review.comment
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Review Delete
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request):

    get_review_id = request.data.get('product_review_id')

    if not get_review_id:
        return Response({'error': 'review_id required'},status= status.HTTP_400_BAD_REQUEST)
    try:
        ProductReview.objects.get(product_review_id=get_review_id).delete()
        return Response({'message': 'Review deleted'}, status=status.HTTP_200_OK)
    
    except ProductReview.DoesNotExist:
        return Response({'error': 'Review not found'},status= status.HTTP_404_NOT_FOUND)