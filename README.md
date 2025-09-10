# Minimarket App

Minimarket es una aplicación web desarrollada con Django para la gestión de productos, usuarios y predicción de stock mediante IA.

## Características

- Dashboard con resumen de productos, usuarios e ingresos.
- Gestión de productos: listado, visualización y predicción de cantidades.
- Chat IA para consultas sobre productos y stock.
- Autenticación de usuarios.
- Interfaz moderna usando TailwindCSS y Phosphor Icons.

## Estructura del Proyecto

- `minimarket/`: Configuración principal de Django.
- `minimark/`: Aplicación principal con modelos, vistas, utilidades y templates.
- `static/`: Archivos estáticos (CSS, imágenes, datos).
- `templates/`: Plantillas HTML para las vistas.
- `utils/predict.py`: Lógica de predicción y procesamiento de mensajes del chat IA.
- `db.sqlite3`: Base de datos SQLite.

## Instalación

1. Clona el repositorio.
2. Instala dependencias:
    ```sh
    pip install -r requirements.txt
    ```
3. Realiza migraciones:
    ```sh
    python manage.py migrate
    ```
4. Ejecuta el servidor:
    ```sh
    python manage.py runserver
    ```

## Uso

- Accede a la página principal para ver el dashboard.
- Navega a "Productos" para gestionar el inventario.
- Usa el "IA Chat" para consultar predicciones de stock.

## Licencia

MIT License. Consulta [LICENSE](LICENSE) para más detalles.