from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from myapp.models import *
from myapp.serializers import *
import random
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta


# Login Buyer & Seller 
@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    
    if not user:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    
    refresh = RefreshToken.for_user(user)
    
    # Check user type
    try:
        seller = Seller.objects.get(user=user)
        user_type = 'seller'
        user_data = {
            "seller_id": seller.seller_id,
            "username": user.username,
            "email": user.email,
            "mobile_no": seller.mobile_no,
            "is_verified": seller.is_verified,}
    except Seller.DoesNotExist:

        try:
            buyer = Buyer.objects.get(user=user)
            user_type = 'buyer'
            user_data = {
                "buyer_id": buyer.buyer_id,
                "username": user.username,
                "email": user.email,
                "mobile_no": buyer.mobile_no}
            
        except Buyer.DoesNotExist:
           
            if user.is_staff or user.is_superuser:
                user_type = 'admin'
                user_data = {
                    # "user_id": user.id,
                    "user_id": user.pk,
                    "username": user.username,
                    "email": user.email,
                    "is_superuser": user.is_superuser,
                    "is_staff": user.is_staff
                }
            else:
                return Response({"error": "User type not recognized"}, status=status.HTTP_400_BAD_REQUEST)
        
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': user_data,
        'user_type': user_type
    }, status= status.HTTP_201_CREATED)


# Log-Out view
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
    
#Forgot password
# @api_view(['POST'])
# def forgot_password(request):
#     email = request.data.get("email")
#     new_password = request.data.get("new_password")
 
#     if not email or not new_password:
#         return Response({"error": "Enter email and new password please!!"}, status=status.HTTP_400_BAD_REQUEST)
#     try:
#         user = User.objects.get(email__iexact=email)
#         user.set_password(new_password)
#         user.save()
#         return Response({"message": "Password Update Success"}, status=status.HTTP_200_OK)
#     except User.DoesNotExist:
#         return Response({"error": "User not exist"}, status= status.HTTP_404_NOT_FOUND)

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(user_email, otp):
    subject = "V-MART OTP for reset password"
    message = f"Hello from V-Mart.\n This is OTP is for reset your password: {otp}"
    from_email = 'vishalsohaliya25@gmail.com'
    recipient_list = [user_email]
    send_mail(subject, message, from_email, recipient_list)

@api_view(['POST'])
def forgot_password_sent_email(request):
    email = request.data.get("email")
    try:
        user = User.objects.get(email__iexact=email)
        otp = generate_otp()
        Forgot_password_otp.objects.create(user=user, otp=otp)
        send_otp_email(email, otp)
        return Response({"message": "OTP sent to your email. Please check your Email box!"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not exist"}, status= status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def reset_password(request):
    email = request.data.get("email")
    otp = request.data.get("otp")
    new_password = request.data.get("new_password")

    try:
        user = User.objects.get(email=email)
        otp_ = Forgot_password_otp.objects.filter(user=user, otp=otp, is_used=False).last()

        if not otp_:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        if timezone.now() - otp_.created_at > timedelta(minutes=10):
            return Response({"OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        otp_.is_used = True
        otp_.save()
        return Response({"Password reset successful"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"Invalid email"}, status= status.HTTP_404_NOT_FOUND)