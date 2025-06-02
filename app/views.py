import jwt
import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET #ensure only GET method is allowed
from django.contrib.auth.hashers import make_password, check_password
from functools import wraps
import json
from .connect import get_db

@csrf_exempt
def signup_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            username = data.get('username')
            password = data.get('password')
            email = data.get('email')

            if not all([username, password, email]):
                return JsonResponse({'error': 'Missing fields'}, status=400)

            db = get_db() # Connect to MongoDB
            users_collection = db["users"]  # ✅ Use "users" collection specifically 
            # Check if user already exists
            if users_collection.find_one({'username': username}):
                return JsonResponse({'error': 'Username already taken'}, status=400)

            # Hash the password
            hashed_password = make_password(password)

            # Save to MongoDB
            users_collection.insert_one({
                'username': username,
                'password': hashed_password,
                'email': email,
                "role": "admin"  # Default role
            })

            return JsonResponse({'message': 'User registered successfully'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST method allowed'}, status=405)

# Secret key (should be kept safe in production)
JWT_SECRET = 'your_secret_key'
JWT_ALGORITHM = 'HS256'

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not all([username, password]):
                return JsonResponse({'error': 'Missing fields'}, status=400)

            db = get_db()
            user = db["users"].find_one({'username': username})

            if not user or not check_password(password, user['password']):
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
             
             
            # Define role from your user document, e.g. user.get('role', 'user')
            role = user.get('role', 'admin')  # or 'admin' if you have a flag


            # Generate JWT token
            payload = {
                'username': username,
                'role': role,  # Add role to the payload
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
            }
            token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

            return JsonResponse({'message': 'Login successful', 'token': token}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST allowed'}, status=405)

def token_required(view_func): # Decorator to protect routes with JWT token
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return JsonResponse({'error': 'Token required'}, status=401)

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM]) # Decode the token using the secret key and algorithm
            db = get_db()
            user = db["users"].find_one({'username': payload['username']}) # Find which user(payload['username']) in the database collection ("users")

            if not user:
                return JsonResponse({'error': 'User not found'}, status=403)

            request.user = user  # optional 
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expired'}, status=403)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=403)

        return view_func(request, *args, **kwargs)
    return wrapped_view

@csrf_exempt
def save_order(request):
    
    if request.method == 'POST':
        
        try:
            data = json.loads(request.body)
             
             # Extract data from the request frontend (model)
            name = data.get('name')
            product = data.get('productName')
            address = data.get('address') #-> ('shoud same from frontend')
            phone = data.get('phone')
            quantity = data.get('quantity')
             
             #error message if any field is missing
            if not all([name, product, address, phone, quantity]):
                return JsonResponse({'error': 'Missing fields'}, status=400)
            
            # Connect to MongoDB
            db = get_db()

            # Insert into MongoDB
            db.orders.insert_one({ #"orders" collection name of database, "insert_one" to insert a single document (record) into the specified collection (in this case, orders).
                'name': name,
                'product': product, #-> : should be same as "model" variable name
                'address': address,
                'phone': phone,
                'quantity': quantity
            })

            return JsonResponse({'message': 'Order saved successfully'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST allowed'}, status=405)

@csrf_exempt
@token_required
def get_orders(request):
    user= request.user  # optional, if you want to use user info
    if request.method == 'GET':
        try:
            db = get_db()
            orders_cursor = db.orders.find() #-> "orders" collection name of database, "find()" to retrieve all documents (records) from the specified collection (in this case, orders).
            orders = [] #empty list to store the orders

            for order in orders_cursor:
                order['_id'] = str(order['_id'])  # Convert ObjectId to string beacause JSON cannot serialize ObjectId, for find() return all data
                orders.append(order)

            return JsonResponse(orders, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only GET allowed'}, status=405)