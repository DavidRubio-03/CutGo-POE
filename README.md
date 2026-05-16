# 🚌 CutGo - Sistema de Gestión de Rutas (Desktop Version)

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-GUI-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red.svg)
![MySQL](https://img.shields.io/badge/MySQL-XAMPP-orange.svg)

Proyecto final para la materia de **Programación Orientada a Eventos (POE)**. 
CutGo es una aplicación de escritorio desarrollada en Python que permite la gestión integral de rutas de transporte, horarios, paradas e incidentes mediante una interfaz gráfica moderna e intuitiva.

---

## 🎯 Características Principales
Esta aplicación demuestra la aplicación práctica de la Programación Orientada a Eventos mediante:
* **Arquitectura de Interfaz:** Uso de `QMainWindow` y `QStackedWidget` para un menú lateral (Sidebar) de navegación fluida.
* **Dashboard Interactivo:** Tarjetas de estadísticas en tiempo real que se actualizan mediante eventos de bases de datos.
* **Módulos de Operación:** Formularios con validación para el "Registro de Horarios" y "Reporte de Incidentes".
* **Gestión de Datos (CRUD):** Paneles de administración para Rutas y Paradas utilizando `QTableWidget` y diálogos modales (`QDialog`) conectados a bases de datos relacionales.
* **Persistencia de Datos:** Integración completa con MySQL utilizando el ORM **SQLAlchemy**.

---

## 🛠️ Tecnologías Utilizadas
* **Lenguaje:** Python 3.x
* **GUI Framework:** PySide6 (Qt for Python)
* **ORM & Base de Datos:** SQLAlchemy + PyMySQL
* **Gestión de Entorno:** `python-dotenv` y entornos virtuales (`venv`).
* **Servidor Local:** XAMPP (Apache & MySQL).

---

## 🚀 Guía de Instalación y Ejecución

Para evaluar y probar este proyecto de manera local, sigue los siguientes pasos:

### 1. Requisitos Previos
* Tener instalado **Python 3.x** en tu sistema.
* Tener instalado **XAMPP** (con los servicios de Apache y MySQL activos).

### 2. Preparación de la Base de Datos
1. Inicia XAMPP y enciende **Apache** y **MySQL**.
2. Ingresa a `http://localhost/phpmyadmin` en tu navegador.
3. Crea una nueva base de datos vacía llamada **`cutgo`** (cotejamiento `utf8mb4_general_ci`).

### 3. Configuración del Proyecto
Clona este repositorio y configura el archivo de entorno:
1. En la raíz del proyecto, asegúrate de tener un archivo llamado `.env` con las siguientes credenciales locales:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=cutgo
   DB_USER=root
   DB_PASSWORD=
(Nota: Se asume que el usuario root de XAMPP no tiene contraseña).

4. Entorno Virtual e Instalación de Dependencias
Abre una terminal en la carpeta raíz del proyecto y ejecuta:

Bash
# 1. Crear el entorno virtual
python -m venv .venv

# 2. Activar el entorno virtual (En Windows)
.\.venv\Scripts\activate

# 3. Instalar los requerimientos del sistema
pip install -r requirements.txt PySide6
5. Poblar la Base de Datos (Seed)
Para poder visualizar la información en las tablas y probar la aplicación, ejecuta el script de sembrado para que SQLAlchemy cree las tablas y las llene con datos de prueba:

Bash
python reseed_db.py
6. Ejecutar la Aplicación
Finalmente, arranca la aplicación de escritorio principal:

Bash
python desktop_app.py
📂 Estructura del Proyecto
/backend: Contiene la lógica del ORM, conexión a BD (database.py) y los modelos de SQLAlchemy (models.py).
/frontend: Archivos legacy de la versión web (React/Vite).
desktop_app.py: Archivo principal de la aplicación GUI (PySide6).
reseed_db.py: Script de automatización para generar esquemas y poblar la base de datos local.
prompts.md: Documentación de la Ingeniería de Prompts utilizada durante el desarrollo.

👥 Equipo de Desarrollo
Proyecto desarrollado por:
Juan David Rubio Salazar
Oscar Guadalupe Rodriguez Olvera
Jocelyn Citlalli Silva Diaz

Asignatura: Programación Orientada a Eventos
