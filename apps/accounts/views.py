from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import UserSerializer
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user with password confirmation
    """
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')  # New field
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    
    # Basic validation
    if not username or not email or not password or not confirm_password:
        return Response(
            {'error': 'Username, email, password, and confirm_password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Password confirmation validation
    if password != confirm_password:
        return Response(
            {'error': 'Passwords do not match'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Password strength validation
    if len(password) < 8:
        return Response(
            {'error': 'Password must be at least 8 characters long'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check for common weak passwords
    common_passwords = ['password', '12345678', 'qwerty123', 'abc12345']
    if password.lower() in common_passwords:
        return Response(
            {'error': 'Password is too common. Please choose a stronger password'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Username validation
    if len(username) < 3:
        return Response(
            {'error': 'Username must be at least 3 characters long'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Email format validation (basic)
    if '@' not in email or '.' not in email:
        return Response(
            {'error': 'Please enter a valid email address'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if username already exists
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists. Please choose a different username'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if email already exists
    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Email already registered. Please use a different email or try logging in'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create user
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        logger.info(f"New user registered: {username}")
        
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(access_token),
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return Response(
            {'error': 'Registration failed. Please try again'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login user and return JWT tokens
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Authenticate user
    user = authenticate(username=username, password=password)
    
    if user is not None:
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        logger.info(f"User logged in: {username}")
        
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(access_token),
            }
        })
    else:
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get current user's profile
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update current user's profile
    """
    user = request.user
    
    # Update fields if provided
    user.first_name = request.data.get('first_name', user.first_name)
    user.last_name = request.data.get('last_name', user.last_name)
    user.email = request.data.get('email', user.email)
    
    try:
        user.save()
        logger.info(f"Profile updated for user: {user.username}")
        return Response({
            'message': 'Profile updated successfully',
            'user': UserSerializer(user).data
        })
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return Response(
            {'error': 'Profile update failed'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )