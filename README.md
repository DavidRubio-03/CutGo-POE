# 🚌 CutGo - Sistema de Gestión de Rutas (Desktop Version)

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-GUI-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red.svg)
![MySQL](https://img.shields.io/badge/MySQL-XAMPP-orange.svg)
![ChartJS](https://img.shields.io/badge/Chart.js-Analytics-pink.svg)
![Leaflet](https://img.shields.io/badge/Leaflet-Maps-lightgreen.svg)

Proyecto final para la materia de **Programación Orientada a Eventos (POE)**. 
CutGo es una aplicación de escritorio desarrollada en Python que permite la gestión integral de rutas de transporte, horarios, paradas e incidentes para la comunidad del CUTonalá, combinando el poder nativo de **PySide6** con la versatilidad de tecnologías web integradas.

---

## 🎯 Características Principales (Arquitectura Híbrida)
Este sistema demuestra un nivel avanzado de Programación Orientada a Eventos e integración de componentes:

* **Seguridad Criptográfica:** Sistema de autenticación de usuarios utilizando la librería `bcrypt` para el hashing y verificación de contraseñas.
* **Interfaz Reactiva y Temas (UI/UX):** Implementación de una barra de navegación superior (Top Navbar) y un sistema global de cambio de tema en tiempo real (**Light / Dark Mode**) mediante inyección dinámica de hojas de estilo (QSS).
* **Gráficas Avanzadas Integradas:** Uso del componente `QWebEngineView` para embeber **Chart.js**, inyectando datos directamente desde consultas SQL de Python hacia JavaScript para generar métricas estadísticas.
* **Mapeo Interactivo:** Renderizado de un mapa dinámico con **Leaflet.js** dentro de la aplicación de escritorio, pintando rutas y marcadores de incidentes calculados en el backend.
* **Formularios Dinámicos (Event-Driven):** Registro de Horarios y Reporte de Incidentes mediante menús desplegables en cascada que consultan la base de datos en tiempo real al cambiar de selección.
* **Persistencia Relacional:** Conexión estricta a base de datos MySQL (XAMPP) gestionada al 100% mediante el ORM **SQLAlchemy**.

---

## 🛠️ Tecnologías Utilizadas
* **Backend / Lógica:** Python 3.x, SQLAlchemy, PyMySQL, Bcrypt.
* **Frontend / GUI Nativa:** PySide6 (Qt for Python).
* **Inyección Web:** HTML5, CSS3, JavaScript (Chart.js, Leaflet) ejecutados vía `QWebEngineView`.
* **Entorno y Base de Datos:** `python-dotenv`, XAMPP (Apache & MySQL).

---

## 🚀 Guía de Instalación y Ejecución

Para evaluar y probar este proyecto de manera local, sigue estos pasos:

### 1. Requisitos Previos
* Tener instalado **Python 3.x**.
* Tener instalado **XAMPP** (con los servicios de Apache y MySQL activos).

### 2. Preparación de la Base de Datos
1. Inicia XAMPP y enciende **Apache** y **MySQL**.
2. Ingresa a `http://localhost/phpmyadmin` en tu navegador.
3. Crea una nueva base de datos vacía llamada **`cutgo`** (cotejamiento `utf8mb4_general_ci`).

### 3. Configuración del Proyecto
Clona este repositorio y asegúrate de tener un archivo llamado `.env` en la raíz del proyecto con las siguientes credenciales locales:
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

# 3. Instalar dependencias
pip install -r requirements.txt PySide6
5. Poblar la Base de Datos (Seed)
Para poder visualizar las gráficas y el mapa con información, ejecuta el script de sembrado (creará las tablas y las llenará con datos de prueba):

Bash
python reseed_db.py
6. Ejecutar la Aplicación
Finalmente, arranca la aplicación de escritorio principal:

Bash
python desktop_app.py
📂 Estructura del Proyecto
/backend: Contiene la lógica del ORM, conexión (database.py) y los modelos (models.py).

desktop_app.py: Archivo principal de la aplicación. Gestiona la GUI, encriptación, y la inyección de componentes web.

reseed_db.py: Script de automatización para generar esquemas y poblar la BD.

prompts.md: Documentación detallada sobre la metodología y la Ingeniería de Prompts utilizada durante el ciclo de desarrollo.

👥 Equipo de Desarrollo
Proyecto estructurado y desarrollado con dedicación por:

- Juan David Rubio Salazar
- Oscar Guadalupe Rodriguez Olvera
- Jocelyn Citlalli Silva Diaz

Asignatura: Programación Orientada a Eventos

Institución: Universidad de Guadalajara (CUTonalá)