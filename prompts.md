# Historial de Prompts - Desarrollo de CutGo Desktop (PySide6)
**Materia:** Programación Orientada a Eventos (POE)
**Estudiante:** [Tu Nombre]

A continuación se documentan los prompts estructurados que se utilizaron en el agente de desarrollo para la construcción de la aplicación de escritorio, demostrando el uso de Arquitectura Orientada a Objetos, manejo de Eventos y conexión a Base de Datos.

---

### Prompt 1: Configuración Base y Conexión a Base de Datos
**Objetivo:** Establecer la conexión con XAMPP utilizando SQLAlchemy y cargar las variables de entorno de forma segura.

> "Actúa como un desarrollador experto en Python y PySide6. Crea el archivo base `desktop_app.py` para mi proyecto CutGo. 
> 1. Configura la carga de variables de entorno usando `python-dotenv`.
> 2. Importa la configuración de la base de datos `SessionLocal` y los modelos SQLAlchemy desde mi carpeta `backend/`.
> 3. Implementa un bloque `try/except` para probar la conexión a MySQL (XAMPP) en el inicio de la app. Si la conexión falla, lanza un evento que muestre un `QMessageBox` de error amigable, en lugar de cerrar la aplicación por consola."

---

### Prompt 2: Estructura de la Interfaz y Menú Lateral (Sidebar)
**Objetivo:** Construir el esqueleto de la aplicación usando `QStackedWidget` para la navegación, aplicando un diseño moderno.

> "Añade una clase `MainWindow` que herede de `QMainWindow`. Necesito una arquitectura de navegación fluida.
> 1. Crea un menú lateral (Sidebar) con botones para: Dashboard, Registro Horario, Incidentes, Admin Rutas y Admin Paradas.
> 2. Usa un `QStackedWidget` como panel central. Cada botón del Sidebar debe estar conectado mediante el evento `.clicked.connect()` para cambiar el índice del `QStackedWidget`.
> 3. Aplica una hoja de estilos (QSS) con un 'Aesthetic Dark Theme' (fondos oscuros `#1e1e2f`, textos claros y acentos de color en los botones al hacer hover)."

---

### Prompt 3: Implementación del Dashboard y Eventos de Actualización
**Objetivo:** Mostrar estadísticas en tiempo real realizando consultas SQL mediante SQLAlchemy.

> "Desarrolla la vista del 'Dashboard' dentro del `QStackedWidget`.
> 1. Crea 4 tarjetas visuales (`QFrame` con `QLabel`) para mostrar totales: Usuarios, Rutas Activas, Horarios Registrados e Incidentes.
> 2. Crea un método `update_dashboard_stats()` que abra una sesión con la base de datos, ejecute consultas `.count()` en los modelos respectivos y actualice el texto de los `QLabel`.
> 3. Agrega un botón 'Actualizar Datos' y enlaza su evento `clicked` a este método. El método también debe llamarse automáticamente al iniciar la aplicación."

---

### Prompt 4: Formularios de Inserción (Eventos y Extracción de Datos)
**Objetivo:** Replicar los formularios de la versión web para ingresar datos a la DB.

> "Desarrolla las vistas para 'Registro Horario' e 'Incidentes'.
> 1. Recrea los formularios basándote en la estructura de mi frontend en React: usa `QComboBox` para seleccionar rutas/usuarios existentes (llenándolos con consultas a la base de datos) y `QLineEdit`/`QDateTimeEdit` para los demás campos.
> 2. Crea un método `save_incidente()` enlazado al botón de guardar. Este método debe instanciar el modelo de SQLAlchemy, capturar los `.text()` y `.currentData()` de los inputs, ejecutar `db.add()` y `db.commit()`.
> 3. Incluye validaciones básicas: si los campos están vacíos, detén el evento y muestra una alerta visual."

---

### Prompt 5: Implementación CRUD Completo (Admin Rutas y Paradas)
**Objetivo:** Cumplir con los requisitos de POE manipulando registros en tiempo real mediante tablas interactivas.

> "Para las vistas de 'Admin Rutas' y 'Admin Paradas', necesito un CRUD completo.
> 1. Agrega un `QTableWidget` en cada vista para listar los registros. Llena la tabla iterando sobre un `db.query(Ruta).all()`.
> 2. Agrega una botonera inferior: 'Crear', 'Editar' y 'Eliminar'.
> 3. Al disparar el evento del botón 'Eliminar', verifica primero qué fila del `QTableWidget` está seleccionada, lanza un cuadro de diálogo de confirmación (`QMessageBox.question`) y, si el usuario acepta, ejecuta el `.delete()` en SQLAlchemy, seguido de un refresco de la tabla."

---

### Prompt 6: Refactorización y Limpieza de Código
**Objetivo:** Asegurar principios SOLID y limpieza para la entrega final.

> "Realiza una revisión final de `desktop_app.py`. Asegúrate de que no haya dependencias externas innecesarias, código muerto ni variables sin usar. Verifica que todos los métodos de base de datos cierren su sesión en un bloque `finally: db.close()` para evitar fugas de memoria, tal como se evaluará en los criterios de POE. El código debe ser estrictamente modular e independiente de cualquier lógica de Inteligencia Artificial previa."