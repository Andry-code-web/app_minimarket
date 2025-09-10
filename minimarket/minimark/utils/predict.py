import pandas as pd
import numpy as np
import os
import ast
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from django.conf import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def preparar_datos():
    # Cargar dataset
    data_path = os.path.join(BASE_DIR, "static", "data", "Retail_Transactions_Dataset.csv")
    datos = pd.read_csv(data_path)
    df = pd.DataFrame(datos)

    # Convertir fecha
    df["Date"] = pd.to_datetime(df["Date"])
    df["Dates"] = df["Date"].dt.date
    df["Times"] = df["Date"].dt.hour

    # Procesar columna Product
    df["Product"] = df["Product"].apply(ast.literal_eval)
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

    # Merge
    df_unidad = df_unidad.merge(
        df_semanal[["semana_lam", "Product", "Unids", "lag_1", "rolling_3"]],
        on=["semana_lam", "Product"],
        how="left"
    )

    return df_unidad


# ==========================
# Predicción para un producto
# ==========================
def predecir_producto(nombre_producto: str):
    df_unidad = preparar_datos()

    # Filtrar producto
    producto_df = df_unidad[df_unidad["Product"] == nombre_producto].copy()

    if producto_df.empty:
        return f"No se encontró el producto '{nombre_producto}' en los datos."

    # Ordenar por fecha
    producto_df["Dates"] = pd.to_datetime(producto_df["Dates"])
    producto_df = producto_df.sort_values("Dates")

    # Features y target
    X = producto_df[["lag_1", "rolling_3"]]
    y = producto_df["Unids_y"]

    # Quitar NaN
    X = X.dropna()
    y = y.loc[X.index]

    if X.empty or y.empty:
        return f"No hay datos suficientes para predecir {nombre_producto}."

    # Entrenar modelo
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Hacer predicción (última semana)
    ultima_fila = X.iloc[[-1]]
    prediccion = model.predict(ultima_fila)[0]

    return round(prediccion, 2)

def extraer_productos(mensaje, lista_productos):
    mensaje = mensaje.lower()
    encontrados = []
    for prod in lista_productos:
        if prod.lower() in mensaje:
            encontrados.append(prod.title())
    return encontrados


def responder_chat(mensaje):
    lista_productos = ["tomates", "Cebolla", "Leche", "Pan", "Arroz"]

    productos_encontrados = extraer_productos(mensaje, lista_productos)

    if not productos_encontrados:
        return "No entendí tu consulta 🤔. ¿Puedes especificar un producto?", []

    resultados = []
    for prod in productos_encontrados:
        pred = predecir_producto(prod)
        if isinstance(pred, str):  # Si devolvió un mensaje de error
            continue
        resultados.append({
            "producto": prod,
            "cantidad": int(pred)
        })

    if not resultados:
        return "No encontré datos suficientes para esos productos 📉", []

    return "Aquí tienes la predicción para tus productos 📊:", resultados

