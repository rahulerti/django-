from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .connect import get_db  # import your MongoDB connection

@csrf_exempt
def save_use(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8')) 
        
        name = data.get('name')
        password = data.get('password')

        db = get_db()
        db.users.insert_one({  # you can change 'users' to any collection name
            "name": name,
            "password": password
        })

        print(name, password)
        return JsonResponse({"message": "Data saved successfully"})
    
    else:
        return JsonResponse({"message": "Invalid request method"})
