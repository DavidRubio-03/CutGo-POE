import sys
import os
import bcrypt
from datetime import datetime
from sqlalchemy import extract, func
from dotenv import load_dotenv

load_dotenv(override=True)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QStackedWidget, QListWidget, QListWidgetItem,
    QComboBox, QMessageBox, QFrame, QGridLayout, QScrollArea
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont

# Imports from backend
from backend.database import SessionLocal
from backend.models import Usuario, Ruta, Parada, RegistroHorario, Incidente

CURRENT_USER_ID = None

def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False

# --- Login View ---

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CutGo - Iniciar Sesión")
        self.resize(450, 550)
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Logo o Título
        title = QLabel("Bienvenido de vuelta")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Ingresa tus datos para continuar")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        
        main_layout.addStretch()
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addSpacing(30)
        
        form_frame = QFrame()
        form_frame.setObjectName("formCard")
        form_layout = QVBoxLayout(form_frame)
        
        lbl_nombre = QLabel("Nombre completo")
        lbl_nombre.setObjectName("fieldLabel")
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Tu nombre completo")
        
        lbl_contra = QLabel("Contraseña")
        lbl_contra.setObjectName("fieldLabel")
        self.txt_contra = QLineEdit()
        self.txt_contra.setEchoMode(QLineEdit.Password)
        self.txt_contra.setPlaceholderText("••••••••")
        
        form_layout.addWidget(lbl_nombre)
        form_layout.addWidget(self.txt_nombre)
        form_layout.addSpacing(15)
        form_layout.addWidget(lbl_contra)
        form_layout.addWidget(self.txt_contra)
        
        main_layout.addWidget(form_frame)
        main_layout.addSpacing(20)
        
        self.btn_login = QPushButton("Iniciar sesión")
        self.btn_login.setObjectName("mainButton")
        self.btn_login.setFixedHeight(50)
        self.btn_login.clicked.connect(self.intentar_login)
        
        main_layout.addWidget(self.btn_login)
        
        self.btn_crear_cuenta = QPushButton("¿Primera vez aquí? Crear cuenta")
        self.btn_crear_cuenta.setObjectName("secondaryButton")
        self.btn_crear_cuenta.setCursor(Qt.PointingHandCursor)
        self.btn_crear_cuenta.clicked.connect(self.abrir_registro)
        
        main_layout.addWidget(self.btn_crear_cuenta, alignment=Qt.AlignCenter)
        main_layout.addStretch()

    def abrir_registro(self):
        self.registro_window = RegistroView()
        self.registro_window.show()

    def intentar_login(self):
        nombre = self.txt_nombre.text().strip()
        contra = self.txt_contra.text()

        if not nombre or not contra:
            QMessageBox.warning(self, "Error", "Por favor ingresa nombre y contraseña.")
            return

        db = SessionLocal()
        try:
            # Primero buscamos por nombre exacto
            usuario = db.query(Usuario).filter(Usuario.nombre == nombre).first()
            
            # Autenticación segura (bcrypt)
            if usuario and verify_password(contra, usuario.contrasena_hash):
                global CURRENT_USER_ID
                CURRENT_USER_ID = usuario.id_usuario
                
                # Iniciar ventana principal
                self.main_window = MainWindow()
                self.main_window.show()
                self.close()
            else:
                QMessageBox.warning(self, "Error", "Nombre o contraseña incorrectos.")
        except Exception as e:
            QMessageBox.critical(self, "Error de BD", f"No se pudo conectar a la base de datos:\n{str(e)}")
        finally:
            db.close()

    def apply_styles(self):
        style_sheet = """
        QMainWindow { background-color: #121212; }
        QLabel { color: #F3F4F6; }
        QLabel#titleLabel { font-size: 28px; font-weight: 900; color: #F3F4F6; letter-spacing: -1px; }
        QLabel#subtitleLabel { font-size: 14px; color: #9CA3AF; font-weight: 300; }
        QLabel#fieldLabel { font-size: 13px; color: #9CA3AF; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
        
        QFrame#formCard { background-color: #1E1E24; border-radius: 16px; padding: 32px; }
        
        QLineEdit {
            background-color: #121212; color: #F3F4F6; border: 1px solid #2C2C35;
            border-radius: 12px; padding: 14px; font-size: 14px;
        }
        QLineEdit:focus { border: 1px solid #FF5C00; }
        
        QPushButton#mainButton { background-color: #F3F4F6; color: #121212; border-radius: 25px; font-size: 15px; font-weight: 800; }
        QPushButton#mainButton:hover { background-color: #FFFFFF; }
        QPushButton#secondaryButton { background-color: transparent; color: #FF5C00; font-size: 13px; font-weight: bold; margin-top: 10px; border: none; }
        QPushButton#secondaryButton:hover { text-decoration: underline; }
        QMessageBox { background-color: #1E1E24; color: white; }
        """
        self.setStyleSheet(style_sheet)


# --- Views Principales ---

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        header_layout = QHBoxLayout()
        title_layout = QVBoxLayout()
        title = QLabel("Panel de Estadísticas")
        title.setObjectName("titleLabel")
        
        date_str = datetime.now().strftime("%A, %d de %B de %Y").upper()
        subtitle = QLabel(date_str)
        subtitle.setObjectName("subtitleLabel")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        layout.addSpacing(40)

        self.grid = QGridLayout()
        self.grid.setSpacing(24)
        
        self.lbl_usuarios = self.create_metric_card("USUARIOS REGISTRADOS", "0", "#FF5C00") 
        self.lbl_rutas = self.create_metric_card("RUTAS ACTIVAS", "0", "#8B5CF6")
        self.lbl_horarios = self.create_metric_card("HORARIOS REGISTRADOS", "0", "#2ECC71")
        self.lbl_incidentes = self.create_metric_card("INCIDENTES ESTE MES", "0", "#E74C3C")

        self.grid.addWidget(self.lbl_usuarios[0], 0, 0)
        self.grid.addWidget(self.lbl_rutas[0], 0, 1)
        self.grid.addWidget(self.lbl_horarios[0], 1, 0)
        self.grid.addWidget(self.lbl_incidentes[0], 1, 1)

        layout.addLayout(self.grid)
        layout.addStretch()

        btn_refresh = QPushButton("Actualizar Datos")
        btn_refresh.setObjectName("actionButton")
        btn_refresh.setFixedWidth(200)
        btn_refresh.clicked.connect(self.load_data)
        layout.addWidget(btn_refresh, alignment=Qt.AlignCenter)

    def create_metric_card(self, title, value, color):
        frame = QFrame()
        frame.setObjectName("metricCard")
        frame.setStyleSheet(f"border-top: 4px solid {color};")
        flayout = QVBoxLayout(frame)
        
        val_label = QLabel(value)
        val_label.setObjectName("metricValue")
        
        title_label = QLabel(title)
        title_label.setObjectName("metricTitle")
        
        flayout.addWidget(val_label)
        flayout.addWidget(title_label)
        return frame, val_label

    def load_data(self):
        db = SessionLocal()
        try:
            total_usuarios = db.query(Usuario).count()
            total_rutas = db.query(Ruta).filter(Ruta.activa.is_(True)).count()
            total_horarios = db.query(RegistroHorario).count()
            
            current_month = datetime.now().month
            incidentes_mes = db.query(Incidente).filter(extract('month', Incidente.fecha_reporte) == current_month).count()

            self.lbl_usuarios[1].setText(str(total_usuarios))
            self.lbl_rutas[1].setText(str(total_rutas))
            self.lbl_horarios[1].setText(str(total_horarios))
            self.lbl_incidentes[1].setText(str(incidentes_mes))
        except Exception as e:
            QMessageBox.critical(self, "Error de Conexión", f"Error cargando dashboard:\n{str(e)}")
        finally:
            db.close()


class RegistroHorarioView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Registro Horario")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Contribuye a la puntualidad de la comunidad.")
        subtitle.setObjectName("subtitleLabel")
        
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addSpacing(30)
        
        form_frame = QFrame()
        form_frame.setObjectName("formCard")
        form_layout = QVBoxLayout(form_frame)
        
        lbl_ruta = QLabel("Seleccionar Ruta")
        lbl_ruta.setObjectName("fieldLabel")
        self.cb_ruta = QComboBox()
        self.cb_ruta.addItem("Buscar ruta...", None)
        self.cb_ruta.currentIndexChanged.connect(self.on_ruta_changed)
        
        lbl_parada = QLabel("Parada")
        lbl_parada.setObjectName("fieldLabel")
        self.cb_parada = QComboBox()
        self.cb_parada.addItem("Seleccionar parada...", None)
        self.cb_parada.setEnabled(False)
        
        form_layout.addWidget(lbl_ruta)
        form_layout.addWidget(self.cb_ruta)
        form_layout.addSpacing(20)
        form_layout.addWidget(lbl_parada)
        form_layout.addWidget(self.cb_parada)
        
        main_layout.addWidget(form_frame)
        main_layout.addSpacing(20)
        
        self.btn_registrar = QPushButton("REGISTRAR PASO AHORA")
        self.btn_registrar.setObjectName("mainButton")
        self.btn_registrar.clicked.connect(self.registrar_horario)
        self.btn_registrar.setFixedHeight(50)
        
        main_layout.addWidget(self.btn_registrar)
        main_layout.addStretch()

    def load_data(self):
        self.cb_ruta.clear()
        self.cb_ruta.addItem("Buscar ruta...", None)
        db = SessionLocal()
        try:
            rutas = db.query(Ruta).filter(Ruta.activa.is_(True)).all()
            for r in rutas:
                self.cb_ruta.addItem(r.nombre_ruta, r.id_ruta)
        except:
            pass
        finally:
            db.close()

    def on_ruta_changed(self):
        self.cb_parada.clear()
        self.cb_parada.addItem("Seleccionar parada...", None)
        id_ruta = self.cb_ruta.currentData()
        
        if not id_ruta:
            self.cb_parada.setEnabled(False)
            return

        db = SessionLocal()
        try:
            self.cb_parada.setEnabled(True)
            paradas = db.query(Parada).filter(Parada.id_ruta == id_ruta).order_by(Parada.orden_en_ruta).all()
            for p in paradas:
                self.cb_parada.addItem(p.nombre_parada, p.id_parada)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las paradas:\n{str(e)}")
        finally:
            db.close()

    def registrar_horario(self):
        id_parada = self.cb_parada.currentData()
        if not id_parada:
            QMessageBox.warning(self, "Atención", "Debes seleccionar una parada.")
            return

        db = SessionLocal()
        try:
            nuevo_registro = RegistroHorario(
                id_parada=id_parada,
                id_usuario=CURRENT_USER_ID,
                timestamp_real=datetime.now()
            )
            db.add(nuevo_registro)
            db.commit()
            QMessageBox.information(self, "Éxito", "¡Registrado con éxito!")
            self.cb_ruta.setCurrentIndex(0)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo al registrar horario:\n{str(e)}")
        finally:
            db.close()


class ReporteIncidenteView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Reportar Incidente")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Tu reporte anónimo ayuda a mantener seguras las rutas.")
        subtitle.setObjectName("subtitleLabel")
        
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addSpacing(30)
        
        form_frame = QFrame()
        form_frame.setObjectName("formCard")
        form_layout = QVBoxLayout(form_frame)
        
        lbl_ruta = QLabel("Filtrar por Ruta (Opcional)")
        lbl_ruta.setObjectName("fieldLabel")
        self.cb_ruta = QComboBox()
        self.cb_ruta.addItem("Todas las rutas...", None)
        self.cb_ruta.currentIndexChanged.connect(self.on_ruta_changed)
        
        lbl_parada = QLabel("¿En qué parada ocurrió?")
        lbl_parada.setObjectName("fieldLabel")
        self.cb_parada = QComboBox()
        self.cb_parada.addItem("Buscar parada...", None)
        
        lbl_tipo = QLabel("Tipo de incidente")
        lbl_tipo.setObjectName("fieldLabel")
        self.cb_tipo = QComboBox()
        self.cb_tipo.addItem("Selecciona el tipo de incidente...", None)
        tipos = [
            ('Robo / Asalto', 'robo'), ('Acoso', 'acoso'), ('Accidente', 'accidente'), 
            ('Camión lleno', 'camion_lleno'), ('Retraso', 'retraso'), ('Otro', 'otro')
        ]
        for label, val in tipos:
            self.cb_tipo.addItem(label, val)
        
        form_layout.addWidget(lbl_ruta)
        form_layout.addWidget(self.cb_ruta)
        form_layout.addSpacing(15)
        form_layout.addWidget(lbl_parada)
        form_layout.addWidget(self.cb_parada)
        form_layout.addSpacing(15)
        form_layout.addWidget(lbl_tipo)
        form_layout.addWidget(self.cb_tipo)
        
        main_layout.addWidget(form_frame)
        main_layout.addSpacing(20)
        
        self.btn_reportar = QPushButton("CONFIRMAR REPORTE")
        self.btn_reportar.setObjectName("mainButton")
        self.btn_reportar.clicked.connect(self.reportar_incidente)
        self.btn_reportar.setFixedHeight(50)
        
        main_layout.addWidget(self.btn_reportar)
        main_layout.addStretch()

    def load_data(self):
        self.cb_ruta.blockSignals(True)
        self.cb_ruta.clear()
        self.cb_ruta.addItem("Todas las rutas...", None)
        db = SessionLocal()
        try:
            rutas = db.query(Ruta).all()
            for r in rutas:
                self.cb_ruta.addItem(r.nombre_ruta, r.id_ruta)
        except:
            pass
        finally:
            self.cb_ruta.blockSignals(False)
            db.close()
            self.load_paradas()

    def on_ruta_changed(self):
        self.load_paradas()

    def load_paradas(self):
        self.cb_parada.clear()
        self.cb_parada.addItem("Buscar parada...", None)
        id_ruta = self.cb_ruta.currentData()
        
        db = SessionLocal()
        try:
            if id_ruta:
                paradas = db.query(Parada).filter(Parada.id_ruta == id_ruta).order_by(Parada.nombre_parada).all()
            else:
                paradas = db.query(Parada).order_by(Parada.nombre_parada).all()
                
            for p in paradas:
                ruta_name = p.ruta.nombre_ruta if p.ruta else "Desconocida"
                self.cb_parada.addItem(f"{p.nombre_parada} ({ruta_name})", p.id_parada)
        except:
            pass
        finally:
            db.close()

    def reportar_incidente(self):
        id_parada = self.cb_parada.currentData()
        tipo = self.cb_tipo.currentData()

        if not id_parada or not tipo:
            QMessageBox.warning(self, "Advertencia", "Debes seleccionar la parada y el tipo de incidente.")
            return

        db = SessionLocal()
        try:
            nuevo_incidente = Incidente(
                id_parada=id_parada,
                id_usuario=CURRENT_USER_ID,
                tipo_incidente=tipo
            )
            db.add(nuevo_incidente)
            db.commit()
            QMessageBox.information(self, "Éxito", "Reporte enviado. Tu contribución ayuda a mantener seguras nuestras rutas.")
            self.cb_ruta.setCurrentIndex(0)
            self.cb_tipo.setCurrentIndex(0)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el incidente:\n{str(e)}")
        finally:
            db.close()


class RouteCard(QFrame):
    clicked = Signal(int)
    def __init__(self, id_ruta):
        super().__init__()
        self.id_ruta = id_ruta
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("routeCard")
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.id_ruta)

class MapaRutasView(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_ruta_id = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Sidebar de Rutas ---
        self.sidebar = QWidget()
        self.sidebar.setObjectName("routesSidebar")
        self.sidebar.setFixedWidth(340)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(24, 24, 16, 24)
        
        title = QLabel("Rutas Activas")
        title.setObjectName("titleLabel")
        title.setStyleSheet("font-size: 20px; font-weight: 800; margin-bottom: 4px;")
        
        subtitle = QLabel("Explora el transporte al CUTonalá")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setStyleSheet("font-size: 13px; margin-bottom: 24px;")
        
        sidebar_layout.addWidget(title)
        sidebar_layout.addWidget(subtitle)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")
        self.routes_layout = QVBoxLayout(self.scroll_content)
        self.routes_layout.setSpacing(16)
        self.routes_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.scroll_content)
        sidebar_layout.addWidget(scroll)
        
        # --- Mapa WebEngine ---
        self.browser = QWebEngineView()
        
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.browser)

    def load_data(self):
        # Limpiar lista
        while self.routes_layout.count():
            item = self.routes_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        db = SessionLocal()
        try:
            rutas = db.query(Ruta).all()
            for r in rutas:
                card = RouteCard(r.id_ruta)
                
                # Highlight si esta seleccionada
                if self.selected_ruta_id == r.id_ruta:
                    card.setStyleSheet("QFrame#routeCard { border: 1px solid #FF5C00; background-color: #2C2C35; }")
                else:
                    if r.activa:
                        card.setStyleSheet("QFrame#routeCard { border: 1px solid #2C2C35; background-color: #1E1E24; }")
                    else:
                        card.setStyleSheet("QFrame#routeCard { border: 1px solid #1E1E24; background-color: #1E1E24; opacity: 0.6; }")
                
                clayout = QVBoxLayout(card)
                clayout.setContentsMargins(16, 12, 16, 12)
                clayout.setSpacing(4)
                
                top_row = QHBoxLayout()
                lbl_num = QLabel(r.numero_camion)
                lbl_num.setStyleSheet("color: #FF5C00; font-weight: bold; font-size: 11px;")
                
                dot = QFrame()
                dot.setFixedSize(8, 8)
                dot.setStyleSheet(f"border-radius: 4px; background-color: {'#2ECC71' if r.activa else '#E74C3C'};")
                
                top_row.addWidget(lbl_num)
                top_row.addStretch()
                top_row.addWidget(dot)
                
                lbl_nombre = QLabel(r.nombre_ruta)
                lbl_nombre.setStyleSheet("font-size: 15px; font-weight: 800; color: #FFFFFF;")
                
                lbl_origen = QLabel(f"📍 {r.municipio_origen or 'Desconocido'}")
                lbl_origen.setStyleSheet("color: #9CA3AF; font-size: 11px;")
                
                clayout.addLayout(top_row)
                clayout.addWidget(lbl_nombre)
                clayout.addWidget(lbl_origen)
                
                card.clicked.connect(self.on_ruta_selected)
                self.routes_layout.addWidget(card)
            
            # Cargar y Renderizar Mapa Leaflet con marcadores
            self.browser.setHtml(self.generate_map_html(db))

        except Exception as e:
            print("Error cargando rutas:", e)
        finally:
            db.close()

    def on_ruta_selected(self, id_ruta):
        if self.selected_ruta_id == id_ruta:
            return
        self.selected_ruta_id = id_ruta
        self.load_data()

    def generate_map_html(self, db):
        markers_js = ""
        polylines_js = ""
        
        if self.selected_ruta_id:
            ruta = db.query(Ruta).filter(Ruta.id_ruta == self.selected_ruta_id).first()
            if ruta:
                paradas_ruta = db.query(Parada).filter(Parada.id_ruta == ruta.id_ruta).order_by(Parada.orden_en_ruta).all()
                if paradas_ruta:
                    ids_paradas = [p.id_parada for p in paradas_ruta]
                    incidentes_query = db.query(Incidente.id_parada, func.count(Incidente.id_incidente)).filter(Incidente.id_parada.in_(ids_paradas)).group_by(Incidente.id_parada).all()
                    incident_map = {p_id: count for p_id, count in incidentes_query}
                    
                    puntos = [f"[{p.latitud}, {p.longitud}]" for p in paradas_ruta if p.latitud and p.longitud]
                    if puntos:
                        polylines_js += f"""
                        L.polyline([{','.join(puntos)}], {{color: '#FF5C00', weight: 4, opacity: 0.8, lineJoin: 'round'}}).addTo(map);
                        """
                        
                    for p in paradas_ruta:
                        if not p.latitud or not p.longitud: continue
                        lat, lon = float(p.latitud), float(p.longitud)
                        count = incident_map.get(p.id_parada, 0)
                        
                        if count == 0:
                            color = "#2ECC71" # Verde
                        elif count <= 2:
                            color = "#F1C40F" # Amarillo
                        else:
                            color = "#E74C3C" # Rojo
                            
                        markers_js += f"""
                        L.circleMarker([{lat}, {lon}], {{
                            color: '#161B22',
                            weight: 2,
                            fillColor: '{color}',
                            fillOpacity: 1,
                            radius: 7
                        }}).bindPopup('<div style="font-family: sans-serif; font-weight: bold; font-size: 14px; margin-bottom: 5px;">{p.nombre_parada}</div><div style="color: {color}; font-size: 11px; font-weight: bold;">{count} Incidentes</div>').addTo(map);
                        """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                body {{ margin: 0; padding: 0; background-color: #121212; }} 
                #map {{ width: 100vw; height: 100vh; }}
                .leaflet-popup-content-wrapper {{ background: #1E1E24; color: #F3F4F6; border-radius: 12px; border: 1px solid #2C2C35; }}
                .leaflet-popup-tip {{ background: #1E1E24; }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                var map = L.map('map', {{zoomControl: false}}).setView([20.5666, -103.2278], 15);
                L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
                    attribution: '© OpenStreetMap contributors'
                }}).addTo(map);
                
                var cutIcon = L.divIcon({{
                  className: 'custom-div-icon',
                  html: `<div style="background-color: #FF5C00; color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 11px; border: 2px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">CUT</div>`,
                  iconSize: [32, 32],
                  iconAnchor: [16, 16]
                }});
                L.marker([20.5666, -103.2278], {{icon: cutIcon}}).addTo(map);

                {polylines_js}
                {markers_js}
            </script>
        </body>
        </html>
        """
        return html


class RegistroView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Crear cuenta")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Solo para estudiantes del CUT")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addSpacing(20)
        
        form_frame = QFrame()
        form_frame.setObjectName("formCard")
        form_frame.setMaximumWidth(600)
        form_layout = QVBoxLayout(form_frame)
        
        lbl_nombre = QLabel("Nombre completo")
        lbl_nombre.setObjectName("fieldLabel")
        self.txt_nombre = QLineEdit()
        
        lbl_carrera = QLabel("Carrera")
        lbl_carrera.setObjectName("fieldLabel")
        self.cb_carrera = QComboBox()
        self.cb_carrera.addItem("Selecciona una carrera...", "")
        self.cb_carrera.addItems(["Ing. en Ciencias Computacionales", "Ing. en Diseño Industrial", 
                                  "Ing. en Nanotecnología", "Medicina", "Enfermería y Obstetricia", 
                                  "Nutrición", "Otra carrera"])
        
        row_layout = QHBoxLayout()
        col1 = QVBoxLayout()
        lbl_semestre = QLabel("Semestre")
        lbl_semestre.setObjectName("fieldLabel")
        self.cb_semestre = QComboBox()
        self.cb_semestre.addItems([str(i) for i in range(1, 11)])
        col1.addWidget(lbl_semestre)
        col1.addWidget(self.cb_semestre)
        
        col2 = QVBoxLayout()
        lbl_municipio = QLabel("Municipio de origen")
        lbl_municipio.setObjectName("fieldLabel")
        self.txt_municipio = QLineEdit()
        col2.addWidget(lbl_municipio)
        col2.addWidget(self.txt_municipio)
        
        row_layout.addLayout(col1)
        row_layout.addLayout(col2)
        
        lbl_contra = QLabel("Contraseña")
        lbl_contra.setObjectName("fieldLabel")
        self.txt_contra = QLineEdit()
        self.txt_contra.setEchoMode(QLineEdit.Password)
        
        lbl_confirma = QLabel("Confirmar contraseña")
        lbl_confirma.setObjectName("fieldLabel")
        self.txt_confirma = QLineEdit()
        self.txt_confirma.setEchoMode(QLineEdit.Password)
        
        form_layout.addWidget(lbl_nombre)
        form_layout.addWidget(self.txt_nombre)
        form_layout.addSpacing(10)
        form_layout.addWidget(lbl_carrera)
        form_layout.addWidget(self.cb_carrera)
        form_layout.addSpacing(10)
        form_layout.addLayout(row_layout)
        form_layout.addSpacing(10)
        form_layout.addWidget(lbl_contra)
        form_layout.addWidget(self.txt_contra)
        form_layout.addSpacing(10)
        form_layout.addWidget(lbl_confirma)
        form_layout.addWidget(self.txt_confirma)
        
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(form_frame)
        center_layout.addStretch()
        
        main_layout.addLayout(center_layout)
        main_layout.addSpacing(20)
        
        self.btn_crear = QPushButton("Crear cuenta")
        self.btn_crear.setObjectName("mainButton")
        self.btn_crear.setFixedWidth(300)
        self.btn_crear.setFixedHeight(50)
        self.btn_crear.clicked.connect(self.crear_cuenta)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_crear, alignment=Qt.AlignCenter)
        main_layout.addLayout(btn_layout)
        main_layout.addStretch()

    def crear_cuenta(self):
        nombre = self.txt_nombre.text().strip()
        carrera = self.cb_carrera.currentText()
        semestre = int(self.cb_semestre.currentText())
        municipio = self.txt_municipio.text().strip()
        contra = self.txt_contra.text()
        confirma = self.txt_confirma.text()

        if not nombre or not carrera or not municipio or not contra:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
            return
        if len(contra) < 6:
            QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 6 caracteres.")
            return
        if contra != confirma:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden.")
            return

        db = SessionLocal()
        try:
            nuevo_usuario = Usuario(
                nombre=nombre,
                carrera=carrera,
                semestre=semestre,
                municipio_origen=municipio,
                contrasena_hash=get_password_hash(contra),
                rol='estudiante'
            )
            db.add(nuevo_usuario)
            db.commit()
            QMessageBox.information(self, "¡Listo!", "Tu cuenta fue creada exitosamente.")
            
            self.txt_nombre.clear()
            self.cb_carrera.setCurrentIndex(0)
            self.cb_semestre.setCurrentIndex(0)
            self.txt_municipio.clear()
            self.txt_contra.clear()
            self.txt_confirma.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo al crear la cuenta:\n{str(e)}")
        finally:
            db.close()


# --- Ventana Principal ---

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CutGo - Desktop App")
        self.resize(1100, 700)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Sidebar ---
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(240)
        
        # Eliminadas las opciones AdminRutas y AdminParadas según lo solicitado
        items = [
            "📊 Panel de Estadísticas", 
            "⏱️ Registro Horario", 
            "⚠️ Reportar Incidente", 
            "🗺️ Mapa Rutas"
        ]
        for item_text in items:
            item = QListWidgetItem(item_text)
            item.setSizeHint(QSize(220, 50))
            self.sidebar.addItem(item)
            
        self.sidebar.currentRowChanged.connect(self.change_view)
        main_layout.addWidget(self.sidebar)

        # --- Contenido Principal ---
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("mainContent")
        
        self.view_dashboard = DashboardView()
        self.view_horarios = RegistroHorarioView()
        self.view_incidentes = ReporteIncidenteView()
        self.view_rutas_activas = MapaRutasView()

        self.stacked_widget.addWidget(self.view_dashboard)
        self.stacked_widget.addWidget(self.view_horarios)
        self.stacked_widget.addWidget(self.view_incidentes)
        self.stacked_widget.addWidget(self.view_rutas_activas)

        main_layout.addWidget(self.stacked_widget)
        
        self.sidebar.setCurrentRow(0)
        self.apply_styles()

    def change_view(self, index):
        self.stacked_widget.setCurrentIndex(index)
        if index == 0:
            self.view_dashboard.load_data()
        elif index == 1:
            self.view_horarios.load_data()
            self.view_horarios.cb_ruta.setCurrentIndex(0)
        elif index == 2:
            self.view_incidentes.load_data()
            self.view_incidentes.cb_ruta.setCurrentIndex(0)
        elif index == 3:
            self.view_rutas_activas.load_data()

    def apply_styles(self):
        style_sheet = """
        QMainWindow { background-color: #121212; }
        
        QListWidget#sidebar {
            background-color: #161B22;
            color: #9CA3AF;
            border: none;
            border-right: 1px solid #2C2C35;
            font-size: 15px;
            font-weight: 600;
            padding-top: 20px;
        }
        QListWidget#sidebar::item { padding-left: 20px; border-radius: 8px; margin: 5px 10px; }
        QListWidget#sidebar::item:selected { background-color: #FF5C00; color: white; }
        QListWidget#sidebar::item:hover:!selected { background-color: #2C2C35; color: white; }
        
        QWidget#mainContent { background-color: #121212; }
        QWidget#routesSidebar { background-color: #161B22; border-right: 1px solid #2C2C35; }
        
        QLabel { color: #F3F4F6; }
        QLabel#titleLabel { font-size: 36px; font-weight: 900; color: #F3F4F6; letter-spacing: -1px; }
        QLabel#subtitleLabel { font-size: 15px; color: #9CA3AF; font-weight: 300; }
        QLabel#fieldLabel { font-size: 13px; color: #9CA3AF; font-weight: bold; text-transform: uppercase; }
        
        QFrame#metricCard { background-color: #1E1E24; border-radius: 16px; padding: 24px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        QLabel#metricValue { font-size: 36px; font-weight: 900; color: #F3F4F6; }
        QLabel#metricTitle { font-size: 13px; color: #9CA3AF; font-weight: bold; margin-top: 6px; letter-spacing: 1px; }
        
        QFrame#formCard { background-color: #1E1E24; border-radius: 16px; padding: 32px; }
        QFrame#routeCard { background-color: #1E1E24; border-radius: 20px; padding: 24px; border: 1px solid #2C2C35; }
        
        QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox {
            background-color: #121212; color: #F3F4F6; border: 1px solid #2C2C35;
            border-radius: 12px; padding: 14px; font-size: 14px;
        }
        QComboBox::drop-down { border: none; }
        QComboBox:disabled { background-color: #161B22; color: #4B5563; opacity: 0.5; }
        QLineEdit:focus, QComboBox:focus { border: 1px solid #FF5C00; }
        
        QPushButton {
            background-color: #2C2C35; color: white; border: none; border-radius: 12px;
            padding: 10px 15px; font-weight: bold; font-size: 14px;
        }
        QPushButton:hover { background-color: #3B3B46; }
        
        QPushButton#mainButton { background-color: #F3F4F6; color: #121212; border-radius: 25px; font-size: 15px; font-weight: 800; }
        QPushButton#mainButton:hover { background-color: #FFFFFF; }
        
        QPushButton#actionButton { background-color: #FF5C00; color: #FFFFFF; border-radius: 25px; font-size: 15px; font-weight: 800; }
        QPushButton#actionButton:hover { background-color: #FF7A30; }
        
        QMessageBox { background-color: #1E1E24; color: white; }
        """
        self.setStyleSheet(style_sheet)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Arrancar con LoginWindow en vez de MainWindow
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec())