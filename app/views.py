from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render 
from django.core.files.storage import default_storage
from django.conf import settings
import json
import os
from .connect import get_db  # Your MongoDB connection
import bcrypt



@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            # Use json.loads to parse the request body
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON format."}, status=400)

        # Ensure both fields are provided
        if not username or not password:
            return JsonResponse({"message": "Both username and password are required."}, status=400)

        # Authenticate using Django's built-in auth system
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user) #login is built in
            return JsonResponse({"message": "Login successful"})
        else:
            return JsonResponse({"message": "Invalid credentials"}, status=401)

    return JsonResponse({"message": "Invalid method"}, status=405)


#session_id = request.COOKIES.get('sessionid') [request.user.is_authenticated to check if the user is logged in.] 


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse JSON data from the body
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON format."}, status=400)
       

        # Ensure both fields are provided
        if not username or not password:
            return JsonResponse({"message": "Both username and password are required."}, status=400)

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({"message": "User already exists"}, status=400)

        try:
            # Create user (password is automatically hashed)
           user=User.objects.create_user(username=username, password=password)


           db=get_db()
           db.new.insert_one({
                "username": username,
                "password":password,
                "email": email,
            })
           return JsonResponse({"message": "User registered successfully"})
        except Exception as e:
              return JsonResponse({"message": f"Error: {str(e)}"}, status=500)

    return render(request, 'signup.html')

#for file upload web page
@csrf_exempt
def save_user(request):
    # Check if the user is authenticated (must be logged in to perform the action)
    if not request.user.is_authenticated:
        return JsonResponse({"message": "You must be logged in to perform this action."}, status=403)

    # Handling POST request (to upload a file)
    if request.method == 'POST' and request.FILES.get('file'):
        # Extract data
        name = request.POST.get('name')
        file = request.FILES.get('file')

        # Ensure all fields are provided
        if not name or not file:
            return JsonResponse({"message": "All fields are required."}, status=400)

        # Check if the user already exists
        if User.objects.filter(username=name).exists():
            return JsonResponse({"message": "User already exists"}, status=400)

        try:
            # Save the file to the media folder
            file_path = default_storage.save(file.name, file)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)

            # Save extra data in MongoDB (assuming db setup is correct)
            db = get_db()  # Make sure you have your MongoDB connection set up
            db.new.insert_one({
                "username": name,
                "file_name": file.name,
                "file_path": full_path
            })

            # Return success response with message and file information
            return JsonResponse({
                "message": "User registered successfully",
                "file_name": file.name,
                "file_path": full_path
            })

        except Exception as e:
            # Catch any errors and return a detailed message
            return JsonResponse({"message": f"Error: {str(e)}"}, status=500)

    # Handling GET request (to retrieve information about the uploaded file)
    elif request.method == 'GET':
        name = request.GET.get('name') #"name" must be same as the frontend input name
       

        # Check if name parameter is provided
        if not name:
            return JsonResponse({"message": "Name is required."}, status=400)

        # Try to retrieve the file information from MongoDB or somewhere else
        try:
            # Assuming you saved file info in MongoDB, fetch the data
            db = get_db()
            user_data = db.new.find_one({"username": name})
            #MongoDB will return the full document, and then you can extract file_name and file_path from that.

            if user_data:
                # Return the file data
                return JsonResponse({
                    "username": user_data["username"],
                    "file_name": user_data["file_name"],
                    "file_path": user_data["file_path"]
                })
            else:
                return JsonResponse({"message": "User not found."}, status=404)

        except Exception as e:
            return JsonResponse({"message": f"Error: {str(e)}"}, status=500)

    # Return an error if neither POST nor GET is used
    return JsonResponse({"message": "Invalid request method."}, status=400)