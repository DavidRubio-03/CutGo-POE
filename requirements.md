# CUT GO — MVP Requirements

## Pantallas del MVP (4 vistas)

### 1. Mapa de Rutas (/)
- Mapa Leaflet centrado en CUT (20.6269, -103.2334, zoom 14)
- Selector de ruta en sidebar izquierdo
- Al seleccionar ruta: dibuja polyline con paradas como markers
- Marker especial para CUT (ícono de campus)
- Click en parada: popup con nombre, próximo camión estimado,
  incidentes activos del día
- Color de marker por nivel de riesgo:
  Verde = 0 incidentes / Amarillo = 1-2 / Rojo = 3+

### 2. Registro de Horario (/horarios)
- Selector de ruta → selector de parada (cascada)
- Fecha/hora (default: ahora)
- Botón "Registrar que el camión pasó AHORA"
- Lista de últimos 5 registros de esa parada hoy
- Cálculo automático: "Próximo camión estimado en ~X min"

### 3. Reportar Incidente (/incidentes)
- Selector de parada (búsqueda por nombre)
- Tipo de incidente (dropdown con los 6 tipos)
- Campo de descripción
- Botón de enviar
- Confirmación visual de envío

### 4. Dashboard Estadísticas (/dashboard)
- 4 cards de métricas: usuarios, rutas, horarios registrados, incidentes este mes
- Gráfica de barras: incidentes por ruta (Chart.js)
- Tabla: top 5 paradas más peligrosas (Query 1)
- Gráfica: frecuencia promedio por parada (Query 2)
- Gráfica: calificación promedio de seguridad por ruta (Query 3)

## 🎨 Guía de Estilo Visual (Apple Native Style)

- **Paleta de Colores:**
  - Primario: #003087 (Azul CUT - para headers y acentos tipográficos)
  - Acento: #E8521A (Naranja CUT - para botones de acción principal y alertas)
  - Fondo: #F2F2F7 (Gris claro tipo iOS)
  - Tarjetas: #FFFFFF (Blanco puro)

- **Componentes:**
  - **Cards:** Esquinas redondeadas (20px), padding generoso, sin bordes (solo sombra suave).
  - **Navegación:** Un "Tab Bar" en la parte inferior para móvil o un Sidebar translúcido (Glassmorphism) para escritorio.
  - **Inputs:** Campos de búsqueda con bordes redondeados y fondo gris sutil.
  - **Botones:** Estilo "Pill" (completamente redondeados en los lados).