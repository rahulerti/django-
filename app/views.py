from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .connect import get_db

@csrf_exempt
def save_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            name = data.get('name')
            product = data.get('productName')
            address = data.get('address')
            phone = data.get('phone')
            quantity = data.get('quantity')

            if not all([name, product, address, phone, quantity]):
                return JsonResponse({'error': 'Missing fields'}, status=400)
            
            db = get_db()

            # Insert into MongoDB
            db.orders.insert_one({ #"orders" collection name of database, "insert_one" to insert a single document (record) into the specified collection (in this case, orders).
                'name': name,
                'product': product,
                'address': address,
                'phone': phone,
                'quantity': quantity
            })

            return JsonResponse({'message': 'Order saved successfully'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST allowed'}, status=405)


def get_orders(request):
    if request.method == 'GET':
        try:
            db = get_db()
            orders_cursor = db.orders.find()
            orders = []

            for order in orders_cursor:
                order['_id'] = str(order['_id'])  # Convert ObjectId to string
                orders.append(order)

            return JsonResponse(orders, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only GET allowed'}, status=405)