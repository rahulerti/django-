from django.shortcuts import render
import json
import jwt
import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET #ensure only GET method is allowed
from django.contrib.auth.hashers import make_password, check_password
from functools import wraps
from .connect import get_user

# Create your views here.
@csrf_exempt
def app_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Signup data received:", data)  # DEBUG

            username = data.get('username')
            password = data.get('password')
            email = data.get('email')

            if not all([username, password, email]):
                return JsonResponse({'error': 'Missing fields'}, status=400)
            db= get_user()  # Connect to MongoDB
            users_collection = db["users"]  # Use "users" collection specifically
            
            # Check if user already exists
            if users_collection.find_one({'username': username}):
                return JsonResponse({'error': 'Username already taken'}, status=400)
            # Hash the password
            hashed_password = make_password(password)

            users_collection.insert_one({
                'username': username,
                'password': hashed_password,
                'email': email,
                "role": "user"  # Default role
            })
      
            return JsonResponse({'message': 'User created successfully'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)

# Secret key (should be kept safe in production)
JWT_SECRET = 'secret_key'
JWT_ALGORITHM = 'HS256'

@csrf_exempt
def app_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not all([username, password]):
                return JsonResponse({'error': 'Missing fields'}, status=400)

            db = get_user()  # Connect to MongoDB
            users_collection = db["users"]

            user = users_collection.find_one({'username': username})
            if not user or not check_password(password, user['password']):
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
            role= user.get('role', 'user')  # Default to 'user' if role not found

            payload = {
                'username': username,
                'role': role,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expiration
            }
            # Generate JWT token (simplified)
            token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
            if isinstance(token, bytes):
             token = token.decode('utf-8')
            
            return JsonResponse({'token': token}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST method allowed'}, status=405)

def app_token(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return JsonResponse({'error': 'Token required'}, status=401)
        
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:] # bearer token is a Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9. remove the "Bearer " part so only token send



        try:
          payload = jwt.decode(
              token,
              JWT_SECRET,
              algorithms=[JWT_ALGORITHM]
          )
          db = get_user()
          users_collection = db["users"].find_one({'username': payload['username']})
          if  not users_collection:
              return JsonResponse({'error': 'User not found'}, status=404)
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        return view_func(request, *args, **kwargs)

    return _wrapped_view

@csrf_exempt #send token by different route
@require_GET
@app_token
def verify_token(request):
    token = request.headers.get('Authorization')
    if token.startswith('Bearer '):
        token = token[7:]

    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    
    return JsonResponse({
        'message': 'Token is valid',
        'username': payload['username'],
        'role': payload['role']
    }, status=200)


