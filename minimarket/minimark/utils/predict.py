import pandas as pd
import numpy as np
import os
import ast
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from django.conf import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Nota: para una aplicación real, sería más eficiente
# preparar los datos una sola vez al iniciar el servidor
# en lugar de cada vez que se hace una predicción.

def preparar_datos():
    """
    Carga y procesa el dataset para su uso en el modelo de predicción.
    """
    # Cargar dataset
    data_path = os.path.join(BASE_DIR, "static", "data", "Retail_Transactions_Dataset.csv")
    try:
        datos = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"Error: El archivo no se encontró en la ruta: {data_path}")
        return None

    df = pd.DataFrame(datos)

    # Convertir fecha
    df["Date"] = pd.to_datetime(df["Date"])
    df["Dates"] = df["Date"].dt.date
    df["Times"] = df["Date"].dt.hour

    # Procesar columna Product
    try:
        df["Product"] = df["Product"].apply(ast.literal_eval)
    except (ValueError, SyntaxError):
        print("Error al procesar la columna 'Product'. Asegúrate de que los datos están en formato de lista.")
        return None

    df_unidad = df.explode("Product").reset_index(drop=True)
    df_unidad["Unids"] = 1
    df_unidad["Dates"] = pd.to_datetime(df_unidad["Dates"])

    # Agregar semana
    df_unidad["semana_lam"] = df_unidad["Dates"].dt.to_period("W").apply(lambda r: r.start_time)

    # Agrupar semanal
    df_semanal = (
        df_unidad.groupby(["semana_lam", "Product"])["Unids"]
        .sum()
        .reset_index()
        .sort_values(["Product", "semana_lam"])
    )

    # Lags
    df_semanal["lag_1"] = df_semanal.groupby("Product")["Unids"].shift(1)
    df_semanal["rolling_3"] = (
        df_semanal.groupby("Product")["Unids"]
        .transform(lambda x: x.shift().rolling(3).mean())
    )

    # Merge para obtener ambas columnas de "Unids"
    df_unidad = df_unidad.merge(
        df_semanal[["semana_lam", "Product", "Unids", "lag_1", "rolling_3"]],
        on=["semana_lam", "Product"],
        how="left"
    )

    return df_unidad

def predecir_producto(nombre_producto: str):
    """
    Predice la venta semanal de un producto específico.
    """
    print(f"Prediciendo para: {nombre_producto}")
    df_unidad = preparar_datos()
    
    if df_unidad is None:
        return "Hubo un error al preparar los datos."

    producto_df = df_unidad[df_unidad["Product"] == nombre_producto].copy()
    print(f"Registros encontrados: {len(producto_df)}")
    
    if producto_df.empty:
        return f"No se encontró el producto '{nombre_producto}' en los datos."

    # Ordenar por fecha y agrupar por semana
    producto_df["Dates"] = pd.to_datetime(producto_df["Dates"])
    producto_df = producto_df.sort_values("Dates")
    
    # Usar las columnas correctas
    X = producto_df[["lag_1", "rolling_3"]].dropna()
    # CAMBIO CRÍTICO: Usar 'Unids_y' que tiene el total semanal, no 'Unids_x' que es siempre 1.
    y = producto_df["Unids_y"].loc[X.index]

    if len(X) < 10:  # Asegurar que tengamos suficientes datos
        return f"No hay suficientes datos históricos para {nombre_producto}."

    # Dividir datos temporalmente
    train_size = int(len(X) * 0.8)
    X_train = X[:train_size]
    X_test = X[train_size:]
    y_train = y[:train_size]
    y_test = y[train_size:]

    if X_train.empty or y_train.empty:
        return f"No hay datos suficientes para predecir {nombre_producto}."

    # Entrenar modelo
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Hacer predicción usando los últimos datos disponibles
    ultima_fila = X.iloc[[-1]]
    prediccion = model.predict(ultima_fila)[0]

    # Validar predicción
    if prediccion < 0:
        prediccion = 0
    
    return round(prediccion)

def extraer_productos(mensaje, lista_productos):
    """Extrae productos de un mensaje de texto."""
    mensaje = mensaje.lower()
    encontrados = []
    for prod in lista_productos:
        if prod.lower() in mensaje:
            encontrados.append(prod.title())
    return encontrados

def responder_chat(mensaje):
    """
    Responde a un mensaje de chat con predicciones de productos.
    """
    productos_map = {
        "Tomatoes": "tomates",
        "Onions": "cebollas",
        "Milk": "leche",
        "Bread": "pan",
        "Rice": "arroz",
        "Eggs": "huevos",
        "Cheese": "queso",
        "Chicken": "pollo",
        "Beef": "carne",
        "Fish": "pescado"
    }

    productos_encontrados = extraer_productos(mensaje, productos_map.keys())

    if not productos_encontrados:
        return "No entendí tu consulta 🤔. ¿Puedes especificar un producto? Por ejemplo: tomates, cebollas, leche, pan, arroz", []

    resultados = []
    for prod in productos_encontrados:
        pred = predecir_producto(prod)
        if isinstance(pred, str):  # Si devolvió un mensaje de error
            print(pred)
            continue
        resultados.append({
            "producto": productos_map.get(prod, prod),
            "cantidad": pred
        })

    if not resultados:
        return "No encontré datos suficientes para esos productos 📉", []

    return "Aquí tienes la predicción semanal para tus productos 📊:", resultados
