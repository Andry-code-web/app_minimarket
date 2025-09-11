from django.shortcuts import render
from .models import Product
from django.shortcuts import render
from .utils.predict import responder_chat

import asyncio
from googletrans import Translator
import inspect

translator = Translator()

# definimos las funciones del traductor
async def _maybe_await(x):
    return await x if inspect.isawaitable(x) else x

async def traducir_texto(texto, dest="en"):
    res = await _maybe_await(translator.translate(texto, dest=dest))
    return res.text

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

        # entonces aqui usamos la traduccion asincrona
        mensaje_en = asyncio.run(traducir_texto(user_message, dest="en"))
        
        if "hello" in mensaje_en.lower():
            respuesta = "¡Hola! 👋 Estoy para ayudarte a gestionar tu stock de productos."
        else:
            respuesta, tabla = responder_chat(mensaje_en)

    return render(request, "chat.html", {
        "title": "IA Chat",
        "user": "Sebastian",
        "active": "underline",
        "user_message": user_message,
        "response": respuesta, 
        "tabla": tabla,
    })
