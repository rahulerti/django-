from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render 
from django.core.files.storage import default_storage
from django.conf import settings
import os
from .connect import get_db  # Your MongoDB connection

@csrf_exempt
def save_user(request):
    if request.method == 'POST' and request.FILES.get('file'):
        # Extract data
        name = request.POST.get('name')
        password = request.POST.get('password')
        file = request.FILES.get('file')

        # Ensure all fields are provided
        if not name or not password or not file:
            return JsonResponse({"message": "All fields are required."}, status=400)

        # Check if user already exists
        if User.objects.filter(username=name).exists():
            return JsonResponse({"message": "User already exists"}, status=400)

        try:
            # Create user (password is automatically hashed)
            user = User.objects.create_user(username=name, password=password)

            # Save the file to media folder
            file_path = default_storage.save(file.name, file)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)

            # Save extra data in MongoDB
            db = get_db()
            db.users.insert_one({
                "username": name,
                "password": password,
                "file_name": file.name,
                "file_path": full_path
            })

            return JsonResponse({"message": "User registered successfully"})

        except Exception as e:
            # Catch any errors and return a detailed message
            return JsonResponse({"message": f"Error: {str(e)}"}, status=500)

    return JsonResponse({"message": "Invalid request. File is missing."}, status=400)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Ensure both fields are provided
        if not username or not password:
            return JsonResponse({"message": "Both username and password are required."}, status=400)

        # Authenticate using Django's built-in auth system
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({"message": "Login successful"})
        else:
            return JsonResponse({"message": "Invalid credentials"}, status=401)

    return render(request, 'login.html') # Render a login form if not a POST request (not need in fetch/ajax/axios)
