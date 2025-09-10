from django.shortcuts import render
from .models import Product
from django.shortcuts import render
from .utils.predict import responder_chat

# Create your views here.
def index(request):
    params = {
        'title': 'Dashboard',
        'user': 'Sebastian',
        'active': 'underline'
    }
    return render(request, 'index.html', params)


def list_products(request):
    products = Product.objects.all()
    params = {
        'title': 'Productos',
        'active': 'underline',
        'user': 'Sebastian',
        'products': products
    }
    return render(request, 'products.html', params)


def chat(request):
    respuesta = None
    tabla = []
    user_message = ""

    if request.method == "POST":
        user_message = request.POST.get("message", "")
        
        if "hola" in user_message.lower():
            respuesta = "¡Hola! 👋 Estoy para ayudarte a gestionar tu stock de productos."
        else:
            respuesta, tabla = responder_chat(user_message)

    return render(request, "chat.html", {
        "title": "IA Chat",
        "user": "Sebastian",
        "active": "underline",
        "user_message": user_message,
        "response": respuesta,  # 👈 cambia a "response" porque en tu HTML usas esa variable
        "tabla": tabla,
    })
