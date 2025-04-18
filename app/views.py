from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import default_storage
import json
import os
from django.conf import settings
from .connect import get_db  # import your MongoDB connection

# models not needed for pymongo 
@csrf_exempt
def save_use(request):
    if request.method == 'POST' and request.FILES.get('file'):
        #Extract data from request
        name = request.POST.get('name')
        password = request.POST.get('password')
        file = request.FILES.get('file')


 # Save file to media folder
        file_path = default_storage.save(file.name, file)
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
        # Save data to MongoDB
        db = get_db()
        db.users.insert_one({  # you can change 'users' to any collection name
            "name": name,
            "password": password,
            "file_name": file.name,
            "file_path": full_path
        })

        print(name, password, file.name)
        return JsonResponse({"message": "Data saved successfully"})
    
    else:
        return JsonResponse({"message": "Invalid request method"})
