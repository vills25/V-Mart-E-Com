# # Buyer register
# User = get_user_model()

# @api_view(['POST'])
# def register_buyer(request):
#     data = request.data
#     required_fields = ['username', 'email', 'password']

#     # Check required fields
#     if not all(field in data for field in required_fields):
#         return Response({"error": "username, email, and password are required."}, status=status.HTTP_400_BAD_REQUEST)

#     username = data['username']
#     email = data['email']
#     password = data['password']

#     if Buyer.objects.filter(username=username).exists():
#         return Response({"error": "Username already exists in Buyer."}, status=status.HTTP_400_BAD_REQUEST)
#     if Buyer.objects.filter(email=email).exists():
#         return Response({"error": "Email already exists in Buyer."}, status=status.HTTP_400_BAD_REQUEST)
#     if User.objects.filter(username=username).exists():
#         return Response({"error": "Username already exists in User."}, status=status.HTTP_400_BAD_REQUEST)

#     # Create User for authentication
#     user = User.objects.create_user(username=username, email=email, password=password)

#     # Create Buyer 
#     buyer = Buyer.objects.create(
#         username=username,
#         email=email,
#         password=user.password,  # hashed password from user
#         first_name=data.get('first_name', ''),
#         last_name=data.get('last_name', ''),
#         ph_number=data.get('ph_number'),
#         address=data.get('address'),)

#     return Response({
#         "message": "Buyer and User created successfully",
#         "buyer": BuyerSerializer(buyer).data
#     }, status=status.HTTP_201_CREATED)

#-------------------------------------------------

# # Login Buyer
# User = get_user_model()

# @api_view(['POST'])
# def login_buyer(request):
#     username = request.data.get('username')
#     password = request.data.get('password')

#     if not username or not password:
#         return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

#     # Authenticate using Django's User model
#     user = authenticate(username=username, password=password)

#     if user is None:
#         return Response({"error": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)

#     # Generate JWT tokens
#     refresh = RefreshToken.for_user(user)

#     # Get corresponding Buyer object
#     try:
#         buyer = Buyer.objects.get(username=username)
#         buyer_data = BuyerSerializer(buyer).data
#     except Buyer.DoesNotExist:
#         buyer_data = None

#     return Response({
#         "refresh": str(refresh),
#         "access": str(refresh.access_token),
#         "buyer": buyer_data
#     }, status=status.HTTP_200_OK)

# --------------------------------------------------------------------

# # Buyer register
# @api_view(['POST'])
# def register_buyer(request):
#     data = request.data
#     if not all(field in data for field in ['buyer_username', 'buyer_email', 'buyer_password']):
#         return Response({"error": "buyer_username, buyer_email, buyer_password required"}, status= status.HTTP_400_BAD_REQUEST)

#     elif Buyer.objects.filter(buyer_username=data['buyer_username']).exists():
#         return Response({"error": "Username already exists"}, status= status.HTTP_400_BAD_REQUEST)
    
#     try:
#         with transaction.atomic():
#             buyer = Buyer.objects.create(
#                 buyer_username=data['buyer_username'],
#                 buyer_first_name=data['buyer_first_name'],
#                 buyer_last_name=data['buyer_last_name'],
#                 buyer_email=data['buyer_email'],
#                 buyer_password=make_password(data['buyer_password']),
#                 buyer_ph_number=data('buyer_ph_number'),
#                 created_by=None,
#                 updated_by=None)
                
#             serializer = BuyerSerializer(buyer)
#             return Response({"message": "Buyer registered", "buyer": serializer.data}, status= status.HTTP_201_CREATED)
        
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# # Buyer Log-In view

# @api_view(['POST'])
# def login_buyer(request):
#     buyer_username = request.data.get('buyer_username')
#     buyer_password = request.data.get('buyer_password')

#     try:

#         if not buyer_username:
#             return Response({'status': 'error', 'message': 'Valid buyer_username is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
#         if not buyer_password:
#             return Response({'status': 'error', 'message': 'buyer_Password is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
#         buyer = Buyer.objects.get(buyer_username=buyer_username, buyer_password=buyer_password)
#         print("----------->>>>>>>>>>>>",buyer.buyer_id)
#         refresh = RefreshToken.for_user(buyer)
#         print("----------->>>>>>>>>>>>",buyer)
#         # refresh['buyer_id'] = buyer.buyer_id

#         tokens = {
#             'refresh': str(refresh),
#             'access': str(refresh.access_token),}
#         return Response({
#                 'status': 'success',
#                 'message': 'Login successful',
#                 'data': tokens,
#             }, status=status.HTTP_200_OK)
                
#     except Buyer.DoesNotExist:
#         return Response({'status': 'error', 'message': 'Buyer not found'}, status=status.HTTP_400_BAD_REQUEST)

#     except Exception as e:
#         return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#---------------------------------------------


# from django.contrib.auth import authenticate
# from rest_framework_simplejwt.tokens import RefreshToken

# @api_view(['POST'])
# def login_buyer(request):
#     buyer_username = request.data.get('buyer_username')
#     buyer_password = request.data.get('buyer_password')

#     user = authenticate(buyer_username=buyer_username, buyer_password=buyer_password)

#     if user is None:
#         return Response({'status': 'error', 'message': 'Invalid credentials'}, status=401)

#     refresh = RefreshToken.for_user(user)

#     return Response({
#         'status': 'success',
#         'message': 'Login successful',
#         'data': {
#             'refresh': str(refresh),
#             'access': str(refresh.access_token)
#         }
#     })