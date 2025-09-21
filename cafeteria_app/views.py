from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Category, MenuItem, Order, OrderItem
from datetime import timedelta

def add_to_order(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)

    order_data = request.session.get('order_data', {})
    if 'items' not in order_data:
        order_data['items'] = []

    found = False
    for order_item in order_data['items']:
        if order_item['item_id'] == item_id:
            order_item['quantity'] += 1
            found = True
            break
    
    if not found:
        order_data['items'].append({'item_id': item_id, 'quantity': 1})
    
    request.session['order_data'] = order_data
    
    return redirect('place_order')

def home(request):
    return render(request, "home.html")

def menu_list(request):
    category_id = request.GET.get("category")
    categories = Category.objects.all()
    items = []
    offers = []

    if category_id == "offers":
        offer_category = Category.objects.filter(name__iexact="Offers").first()
        if offer_category:
            offers = MenuItem.objects.filter(category=offer_category, is_available=True)
    elif category_id:
        items = MenuItem.objects.filter(category_id=category_id, is_available=True)
    else:
        offer_category = Category.objects.filter(name__iexact="Offers").first()
        if offer_category:
            offers = MenuItem.objects.filter(category=offer_category, is_available=True)
        
    return render(request, "menu.html", {
        "categories": categories,
        "items": items,
        "offers": offers
    })

def place_order(request):
    if request.method == "POST":
        order_data = request.session.get('order_data', {})
        if 'items' not in order_data:
            order_data['items'] = []
            
        ordered_item_ids = [item['item_id'] for item in order_data['items']]
        
        for item_id, quantity_str in request.POST.items():
            if item_id.startswith('quantity-'):
                item_id = item_id.replace('quantity-', '')
                quantity = int(quantity_str)
                
                found = False
                for item in order_data['items']:
                    if str(item['item_id']) == item_id:
                        item['quantity'] = quantity
                        found = True
                        break
                if not found:
                    order_data['items'].append({'item_id': int(item_id), 'quantity': quantity})
                
                order_data['items'] = [item for item in order_data['items'] if item['quantity'] > 0]
        
        order_data['customer_name'] = request.POST.get("customer_name")
        order_data['email'] = request.POST.get("email")
        order_data['phone'] = request.POST.get("phone")
        request.session['order_data'] = order_data

        return redirect('check_your_order')

    else:
        ordered_items = []
        ordered_item_ids = []
        order_data = request.session.get('order_data', {})
        
        if 'items' in order_data:
            for item in order_data['items']:
                menu_item = get_object_or_404(MenuItem, id=item['item_id'])
                ordered_items.append({'menu_item': menu_item, 'quantity': item['quantity']})
                ordered_item_ids.append(item['item_id'])

        available_items = MenuItem.objects.filter(is_available=True).exclude(id__in=ordered_item_ids)

        return render(request, "order_form.html", {
            "ordered_items": ordered_items,"available_items": available_items
        })


def confirm_order(request):
    data = request.session.get('order_data')
    if not data:
        return redirect('place_order')

    order = Order.objects.create(
        customer_name=data.get("customer_name", "Anonymous"),
        status="PENDING",
        created_at=timezone.now(),
        updated_at=timezone.now(),
    )

    for entry in data["items"]:
        menu_item = MenuItem.objects.get(id=entry["item_id"])
        OrderItem.objects.create(
            order=order,
            menu_item=menu_item,
            quantity=entry["quantity"]
        )

    del request.session['order_data'] 

    expected_time = timezone.now() + timedelta(minutes=20)
    context = {
        "order_number": order.id,
        "expected_time": expected_time.strftime("%H:%M")
    }

    return render(request, "thanks.html", context)


def check_your_order(request):
    data = request.session.get('order_data')
    if not data or 'items' not in data:
        return redirect('place_order')
    
    selected_items = []
    total_price = 0
    
    for entry in data['items']:
        try:
            menu_item = MenuItem.objects.get(id=entry['item_id'])
            qty = entry['quantity']
            if qty > 0:
                selected_items.append((menu_item, qty))
                total_price += menu_item.price * qty
        except MenuItem.DoesNotExist:
            continue

    context = {
        "customer_name": data.get("customer_name", ""),
        "email": data.get("email", ""),
        "phone": data.get("phone", ""),
        "items": selected_items,
        "total_price": total_price
    }

    return render(request, "check_your_order.html", context)



def thanks(request):
    return render(request, "thanks.html", {"order_number": None, "expected_time": None})

def register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        return redirect("thanks")
    return render(request, "register.html")