# Evolución del Desarrollo Asistido por IA - CutGo Desktop
**Proyecto:** Sistema de Gestión de Rutas (PySide6 + SQLAlchemy)
**Materia:** Programación Orientada a Eventos (POE)
**Equipo:** Juan David Rubio Salazar, Oscar Guadalupe Rodriguez Olvera, Jocelyn Citlalli Silva Diaz

A continuación se detalla la metodología de Ingeniería de Prompts utilizada para el desarrollo del sistema. El proyecto se construió bajo un enfoque de **Desarrollo Iterativo**, dividiendo el sistema en módulos lógicos para asegurar la integridad de la base de datos y la escalabilidad de la interfaz gráfica.

---

## FASE 1: Configuración del Entorno y Conexión a Base de Datos
**Objetivo:** Establecer una conexión segura a MySQL (XAMPP) usando variables de entorno, evitando exponer credenciales en el código fuente.

**Prompt utilizado:**
> "Actúa como un experto de Software en Python. Necesito configurar la capa de persistencia para una aplicación de escritorio llamada CutGo. 
> 1. Utiliza `SQLAlchemy` para mapear las tablas de mi base de datos MySQL (Usuarios, Rutas, Paradas, Registros, Incidentes). 
> 2. Implementa `python-dotenv` para cargar las credenciales desde un archivo `.env` local. 
> 3. Construye un archivo `database.py` que exporte un `SessionLocal` con un bloque `try/except` robusto, de modo que si el servidor de XAMPP está apagado, la aplicación lance una alerta visual en lugar de cerrarse abruptamente por consola."

*Justificación técnica:* Se garantizó la seguridad (cero contraseñas hardcodeadas) y se aplicó el patrón de diseño Singleton para el manejo de sesiones de base de datos.

---

## FASE 2: Autenticación Segura y Estructura Base (PySide6)
**Objetivo:** Crear el primer punto de interacción visual (Login) e implementar seguridad en las contraseñas antes de dar acceso al sistema.

**Prompt utilizado:**
> "Vamos a comenzar con la interfaz gráfica usando `PySide6`. 
> 1. Crea una clase `LoginWindow` que herede de `QMainWindow`. Necesito un formulario con campos para Nombre y Contraseña.
> 2. Integra la librería `bcrypt`. Al momento de presionar el botón de inicio de sesión, el sistema debe consultar la tabla de Usuarios mediante SQLAlchemy y verificar el hash de la contraseña.
> 3. Si la validación es exitosa, guarda el ID y Nombre del usuario en variables globales (para auditar quién hace los registros más adelante), cierra la ventana de Login y abre una nueva clase vacía llamada `MainWindow`."

*Justificación técnica:* El uso de `bcrypt` demuestra conocimiento en ciberseguridad básica, evitando guardar o comparar contraseñas en texto plano.

---

## FASE 3: Desarrollo de Módulos Operativos (Eventos e Inserciones)
**Objetivo:** Recrear los formularios de "Registro de Horarios" y "Reporte de Incidentes", conectando los componentes visuales con operaciones CRUD.

**Prompt utilizado:**
> "Desarrolla las vistas para 'RegistroHorarioView' y 'ReporteIncidenteView' utilizando `QComboBox` dependientes (encadenados). 
> 1. Al cargar la vista, el primer ComboBox debe llenarse con las rutas activas haciendo un `.query(Ruta).all()`.
> 2. Usa el evento `currentIndexChanged.connect()` para que, al seleccionar una ruta, se dispare una consulta a la base de datos que llene el segundo ComboBox únicamente con las Paradas que pertenecen a esa ruta.
> 3. Al presionar 'Confirmar', recolecta los IDs, utiliza el ID del usuario logueado en la sesión actual, e inserta el nuevo registro en la base de datos usando `db.add()` y `db.commit()`."

*Justificación técnica:* Aquí se aplicó fuertemente la Programación Orientada a Eventos, haciendo que la interfaz reaccione y consulte la base de datos dinámicamente según las acciones del usuario.

---

## FASE 4: Superando Limitaciones de PySide6 (Integración Web)
**Objetivo:** Las librerías nativas de Qt para mapas y gráficas son limitadas visualmente. Se buscó una solución híbrida para integrar Leaflet y Chart.js en la app de escritorio y lograr paridad 1:1 con la versión web original.

**Prompt utilizado:**
> "Necesito renderizar un mapa interactivo y gráficas dinámicas dentro de mi aplicación de PySide6 para mantener el mismo diseño que mi versión web original.
> 1. Implementa el widget `QWebEngineView`.
> 2. Crea un método que lea las coordenadas (Latitud/Longitud) de la tabla 'Paradas' y cuente cuántos incidentes tiene cada parada usando `func.count()` y `group_by()` en SQLAlchemy.
> 3. Genera un string HTML/JS interno que importe `Leaflet` (para el mapa) y `Chart.js` (para estadísticas). Inyecta los datos de Python en el código de JavaScript mediante f-strings para renderizar marcadores de colores según la cantidad de incidentes.
> 4. Carga este HTML en el `QWebEngineView` mediante el método `.setHtml()`."

*Justificación técnica:* Se demostró capacidad analítica al integrar tecnologías de frontend web dentro de un ecosistema de escritorio (Python/C++), resolviendo el problema de renderizado avanzado sin dependencias nativas pesadas.

---

## FASE 5: Refactorización Final de UI/UX (Top Navbar y Temas)
**Objetivo:** Modernizar la interfaz, reemplazar el menú lateral por una barra superior de navegación e implementar un sistema global de Modo Claro / Oscuro reactivo.

**Prompt utilizado:**
> "Rediseña la arquitectura de navegación en `MainWindow`. 
> 1. Elimina el menú lateral (`QListWidget`) y crea un `QFrame` superior (Top Navbar) que contenga los botones de navegación horizontalmente. Conecta estos botones a un `QStackedWidget` para cambiar de vista.
> 2. Implementa un sistema de gestión de temas definiendo dos diccionarios: `DARK_THEME` y `LIGHT_THEME` con variables de colores (bg_main, text_primary, accent, etc.).
> 3. Agrega un botón de interruptor (☀️/🌙). Al presionarlo, debe disparar un evento que actualice toda la hoja de estilos global (`setStyleSheet`) usando las variables del diccionario activo, y que vuelva a inyectar estos colores en el HTML de los `QWebEngineView` para que las gráficas y el mapa también cambien de color en tiempo real."

*Justificación técnica:* Se consolidó una arquitectura de software limpia. El sistema de temas demuestra un manejo avanzado de actualización de estado y manipulación de DOM interno en componentes embebidos.