import sys
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit, QLineEdit,
    QPushButton, QLabel, QStackedWidget, QListWidget, QListWidgetItem,
    QComboBox, QMessageBox, QFrame, QGridLayout, QCheckBox, QAbstractItemView,
    QDoubleSpinBox, QSpinBox, QDialog, QDialogButtonBox, QDateTimeEdit, QFormLayout
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont

# Imports from backend
from backend.database import SessionLocal
from backend.models import Usuario, Ruta, Parada, RegistroHorario, Incidente

# Usuario simulado
SIMULATED_USER_ID = 1


class RutaDialog(QDialog):
    def __init__(self, parent=None, ruta=None):
        super().__init__(parent)
        self.setWindowTitle("Crear/Editar Ruta")
        self.setMinimumWidth(400)
        self.ruta = ruta
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        
        self.txt_nombre = QLineEdit()
        self.txt_camion = QLineEdit()
        self.txt_origen = QLineEdit()
        self.chk_activa = QCheckBox("Activa")
        self.chk_activa.setChecked(True)

        if self.ruta:
            self.txt_nombre.setText(self.ruta.nombre_ruta)
            self.txt_camion.setText(self.ruta.numero_camion)
            self.txt_origen.setText(self.ruta.municipio_origen or "")
            self.chk_activa.setChecked(self.ruta.activa)

        layout.addRow("Nombre de Ruta:", self.txt_nombre)
        layout.addRow("No. Camión:", self.txt_camion)
        layout.addRow("Origen:", self.txt_origen)
        layout.addRow("", self.chk_activa)

        self.btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.btn_box.accepted.connect(self.accept)
        self.btn_box.rejected.connect(self.reject)
        layout.addRow(self.btn_box)

    def get_data(self):
        return {
            "nombre_ruta": self.txt_nombre.text().strip(),
            "numero_camion": self.txt_camion.text().strip(),
            "municipio_origen": self.txt_origen.text().strip(),
            "activa": self.chk_activa.isChecked()
        }


class ParadaDialog(QDialog):
    def __init__(self, parent=None, parada=None, id_ruta=None):
        super().__init__(parent)
        self.setWindowTitle("Crear/Editar Parada")
        self.setMinimumWidth(400)
        self.parada = parada
        self.id_ruta = id_ruta
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        
        self.txt_nombre = QLineEdit()
        self.sp_lat = QDoubleSpinBox()
        self.sp_lat.setRange(-90, 90)
        self.sp_lat.setDecimals(6)
        
        self.sp_lon = QDoubleSpinBox()
        self.sp_lon.setRange(-180, 180)
        self.sp_lon.setDecimals(6)

        self.sp_orden = QSpinBox()
        self.sp_orden.setRange(1, 100)
        
        self.chk_terminal = QCheckBox("Es Terminal")

        if self.parada:
            self.txt_nombre.setText(self.parada.nombre_parada)
            self.sp_lat.setValue(float(self.parada.latitud))
            self.sp_lon.setValue(float(self.parada.longitud))
            self.sp_orden.setValue(self.parada.orden_en_ruta)
            self.chk_terminal.setChecked(self.parada.es_terminal)

        layout.addRow("Nombre Parada:", self.txt_nombre)
        layout.addRow("Latitud:", self.sp_lat)
        layout.addRow("Longitud:", self.sp_lon)
        layout.addRow("Orden en Ruta:", self.sp_orden)
        layout.addRow("", self.chk_terminal)

        self.btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.btn_box.accepted.connect(self.accept)
        self.btn_box.rejected.connect(self.reject)
        layout.addRow(self.btn_box)

    def get_data(self):
        return {
            "id_ruta": self.id_ruta,
            "nombre_parada": self.txt_nombre.text().strip(),
            "latitud": self.sp_lat.value(),
            "longitud": self.sp_lon.value(),
            "orden_en_ruta": self.sp_orden.value(),
            "es_terminal": self.chk_terminal.isChecked()
        }


class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Dashboard de Estadísticas")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        layout.addSpacing(20)

        self.grid = QGridLayout()
        self.grid.setSpacing(20)
        
        self.lbl_usuarios = self.create_metric_card("Usuarios", "0", "#00d2ff")
        self.lbl_rutas = self.create_metric_card("Rutas Activas", "0", "#8B5CF6")
        self.lbl_horarios = self.create_metric_card("Registros Horario", "0", "#2ECC71")
        self.lbl_incidentes = self.create_metric_card("Incidentes", "0", "#E74C3C")

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
            total_incidentes = db.query(Incidente).count()

            self.lbl_usuarios[1].setText(str(total_usuarios))
            self.lbl_rutas[1].setText(str(total_rutas))
            self.lbl_horarios[1].setText(str(total_horarios))
            self.lbl_incidentes[1].setText(str(total_incidentes))
        except Exception as e:
            QMessageBox.critical(self, "Error de Conexión", f"Error cargando dashboard:\n{str(e)}")
        finally:
            db.close()


class RegistroHorarioView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_rutas()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Registro de Horario")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        layout.addSpacing(20)

        self.cb_ruta = QComboBox()
        self.cb_ruta.addItem("Selecciona una ruta...", None)
        self.cb_ruta.currentIndexChanged.connect(self.on_ruta_changed)
        layout.addWidget(QLabel("Ruta:"))
        layout.addWidget(self.cb_ruta)
        
        layout.addSpacing(15)

        self.cb_parada = QComboBox()
        self.cb_parada.addItem("Selecciona una parada...", None)
        self.cb_parada.setEnabled(False)
        layout.addWidget(QLabel("Parada:"))
        layout.addWidget(self.cb_parada)

        layout.addSpacing(15)

        self.dt_tiempo = QDateTimeEdit()
        self.dt_tiempo.setDateTime(datetime.now())
        self.dt_tiempo.setCalendarPopup(True)
        layout.addWidget(QLabel("Fecha y Hora de registro:"))
        layout.addWidget(self.dt_tiempo)

        layout.addSpacing(30)

        self.btn_registrar = QPushButton("GUARDAR REGISTRO")
        self.btn_registrar.setObjectName("actionButton")
        self.btn_registrar.clicked.connect(self.registrar_horario)
        layout.addWidget(self.btn_registrar)
        layout.addStretch()

    def load_rutas(self):
        db = SessionLocal()
        try:
            rutas = db.query(Ruta).filter(Ruta.activa.is_(True)).all()
            for r in rutas:
                self.cb_ruta.addItem(r.nombre_ruta, r.id_ruta)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las rutas:\n{str(e)}")
        finally:
            db.close()

    def on_ruta_changed(self):
        self.cb_parada.clear()
        self.cb_parada.addItem("Selecciona una parada...", None)
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
            dt_value = self.dt_tiempo.dateTime().toPython()
            nuevo_registro = RegistroHorario(
                id_parada=id_parada,
                id_usuario=SIMULATED_USER_ID,
                timestamp_real=dt_value
            )
            db.add(nuevo_registro)
            db.commit()
            QMessageBox.information(self, "Éxito", "¡Registro de horario guardado correctamente!")
            self.cb_ruta.setCurrentIndex(0)
            self.dt_tiempo.setDateTime(datetime.now())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo al registrar horario:\n{str(e)}")
        finally:
            db.close()


class ReporteIncidenteView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_rutas()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Reporte de Incidente")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        layout.addSpacing(20)

        self.cb_ruta = QComboBox()
        self.cb_ruta.addItem("Selecciona una ruta...", None)
        self.cb_ruta.currentIndexChanged.connect(self.on_ruta_changed)
        layout.addWidget(QLabel("Ruta del incidente:"))
        layout.addWidget(self.cb_ruta)
        
        layout.addSpacing(10)

        self.cb_parada = QComboBox()
        self.cb_parada.addItem("Selecciona una parada...", None)
        self.cb_parada.setEnabled(False)
        layout.addWidget(QLabel("Parada más cercana:"))
        layout.addWidget(self.cb_parada)

        layout.addSpacing(10)

        self.cb_tipo = QComboBox()
        tipos = ['robo', 'acoso', 'accidente', 'camion_lleno', 'retraso', 'otro']
        self.cb_tipo.addItem("Selecciona el tipo de incidente...", None)
        for t in tipos:
            self.cb_tipo.addItem(t.capitalize(), t)
        layout.addWidget(QLabel("Nivel de gravedad / Tipo:"))
        layout.addWidget(self.cb_tipo)

        layout.addSpacing(10)

        self.txt_desc = QTextEdit()
        self.txt_desc.setPlaceholderText("Describe los detalles del incidente aquí...")
        self.txt_desc.setMaximumHeight(100)
        layout.addWidget(QLabel("Descripción detallada:"))
        layout.addWidget(self.txt_desc)

        layout.addSpacing(20)

        self.btn_reportar = QPushButton("ENVIAR REPORTE")
        self.btn_reportar.setObjectName("dangerButton")
        self.btn_reportar.clicked.connect(self.reportar_incidente)
        layout.addWidget(self.btn_reportar)
        layout.addStretch()

    def load_rutas(self):
        db = SessionLocal()
        try:
            rutas = db.query(Ruta).all()
            for r in rutas:
                self.cb_ruta.addItem(r.nombre_ruta, r.id_ruta)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar rutas:\n{str(e)}")
        finally:
            db.close()

    def on_ruta_changed(self):
        self.cb_parada.clear()
        self.cb_parada.addItem("Selecciona una parada...", None)
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
            QMessageBox.critical(self, "Error", f"Error al cargar paradas:\n{str(e)}")
        finally:
            db.close()

    def reportar_incidente(self):
        id_parada = self.cb_parada.currentData()
        tipo = self.cb_tipo.currentData()

        if not id_parada or not tipo:
            QMessageBox.warning(self, "Advertencia", "Debes seleccionar parada y tipo de incidente.")
            return

        db = SessionLocal()
        try:
            nuevo_incidente = Incidente(
                id_parada=id_parada,
                id_usuario=SIMULATED_USER_ID,
                tipo_incidente=tipo,
                descripcion=self.txt_desc.toPlainText().strip()
            )
            db.add(nuevo_incidente)
            db.commit()
            QMessageBox.information(self, "Éxito", "Incidente reportado exitosamente.")
            self.cb_ruta.setCurrentIndex(0)
            self.cb_tipo.setCurrentIndex(0)
            self.txt_desc.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el incidente:\n{str(e)}")
        finally:
            db.close()


class AdminRutasView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Administración de Rutas")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        btn_crear = QPushButton("Crear Ruta")
        btn_editar = QPushButton("Editar Seleccionada")
        btn_eliminar = QPushButton("Eliminar Seleccionada")
        btn_crear.clicked.connect(self.action_crear)
        btn_editar.clicked.connect(self.action_editar)
        btn_eliminar.clicked.connect(self.action_eliminar)
        
        toolbar.addWidget(btn_crear)
        toolbar.addWidget(btn_editar)
        toolbar.addWidget(btn_eliminar)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Camión", "Origen", "Activa"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

    def load_data(self):
        self.table.setRowCount(0)
        db = SessionLocal()
        try:
            rutas = db.query(Ruta).all()
            for r in rutas:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(r.id_ruta)))
                self.table.setItem(row, 1, QTableWidgetItem(r.nombre_ruta))
                self.table.setItem(row, 2, QTableWidgetItem(r.numero_camion))
                self.table.setItem(row, 3, QTableWidgetItem(r.municipio_origen or ""))
                self.table.setItem(row, 4, QTableWidgetItem("Sí" if r.activa else "No"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar rutas:\n{str(e)}")
        finally:
            db.close()

    def action_crear(self):
        dialog = RutaDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data['nombre_ruta'] or not data['numero_camion']:
                QMessageBox.warning(self, "Error", "Nombre y Camión son obligatorios.")
                return
            db = SessionLocal()
            try:
                nueva = Ruta(**data)
                db.add(nueva)
                db.commit()
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo crear:\n{str(e)}")
            finally:
                db.close()

    def action_editar(self):
        selected = self.table.selectedItems()
        if not selected: return
        id_ruta = int(self.table.item(selected[0].row(), 0).text())
        
        db = SessionLocal()
        try:
            ruta = db.query(Ruta).filter(Ruta.id_ruta == id_ruta).first()
            if not ruta: return
            
            dialog = RutaDialog(self, ruta=ruta)
            if dialog.exec():
                data = dialog.get_data()
                if not data['nombre_ruta'] or not data['numero_camion']:
                    QMessageBox.warning(self, "Error", "Nombre y Camión son obligatorios.")
                    return
                for key, val in data.items():
                    setattr(ruta, key, val)
                db.commit()
                self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo editar:\n{str(e)}")
        finally:
            db.close()

    def action_eliminar(self):
        selected = self.table.selectedItems()
        if not selected: return
        id_ruta = int(self.table.item(selected[0].row(), 0).text())
        
        resp = QMessageBox.question(self, "Confirmar", "¿Eliminar esta ruta y todas sus dependencias?")
        if resp == QMessageBox.Yes:
            db = SessionLocal()
            try:
                ruta = db.query(Ruta).filter(Ruta.id_ruta == id_ruta).first()
                if ruta:
                    db.delete(ruta)
                    db.commit()
                    self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar:\n{str(e)}")
            finally:
                db.close()


class AdminParadasView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Administración de Paradas")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        filter_layout = QHBoxLayout()
        self.cb_ruta_filter = QComboBox()
        self.cb_ruta_filter.addItem("Seleccione una ruta para ver sus paradas...", None)
        self.cb_ruta_filter.currentIndexChanged.connect(self.load_paradas)
        filter_layout.addWidget(QLabel("Filtrar Ruta:"))
        filter_layout.addWidget(self.cb_ruta_filter)
        layout.addLayout(filter_layout)

        toolbar = QHBoxLayout()
        btn_crear = QPushButton("Crear Parada")
        btn_editar = QPushButton("Editar Seleccionada")
        btn_eliminar = QPushButton("Eliminar Seleccionada")
        btn_crear.clicked.connect(self.action_crear)
        btn_editar.clicked.connect(self.action_editar)
        btn_eliminar.clicked.connect(self.action_eliminar)
        
        toolbar.addWidget(btn_crear)
        toolbar.addWidget(btn_editar)
        toolbar.addWidget(btn_eliminar)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Lat", "Lon", "Orden", "Terminal"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

    def load_rutas(self):
        self.cb_ruta_filter.blockSignals(True)
        self.cb_ruta_filter.clear()
        self.cb_ruta_filter.addItem("Seleccione una ruta para ver sus paradas...", None)
        db = SessionLocal()
        try:
            rutas = db.query(Ruta).all()
            for r in rutas:
                self.cb_ruta_filter.addItem(r.nombre_ruta, r.id_ruta)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar rutas:\n{str(e)}")
        finally:
            db.close()
            self.cb_ruta_filter.blockSignals(False)
            self.table.setRowCount(0)

    def load_paradas(self):
        id_ruta = self.cb_ruta_filter.currentData()
        self.table.setRowCount(0)
        if not id_ruta: return

        db = SessionLocal()
        try:
            paradas = db.query(Parada).filter(Parada.id_ruta == id_ruta).order_by(Parada.orden_en_ruta).all()
            for p in paradas:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(p.id_parada)))
                self.table.setItem(row, 1, QTableWidgetItem(p.nombre_parada))
                self.table.setItem(row, 2, QTableWidgetItem(str(p.latitud)))
                self.table.setItem(row, 3, QTableWidgetItem(str(p.longitud)))
                self.table.setItem(row, 4, QTableWidgetItem(str(p.orden_en_ruta)))
                self.table.setItem(row, 5, QTableWidgetItem("Sí" if p.es_terminal else "No"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar paradas:\n{str(e)}")
        finally:
            db.close()

    def action_crear(self):
        id_ruta = self.cb_ruta_filter.currentData()
        if not id_ruta:
            QMessageBox.warning(self, "Atención", "Seleccione una ruta primero.")
            return

        dialog = ParadaDialog(self, id_ruta=id_ruta)
        if dialog.exec():
            data = dialog.get_data()
            if not data['nombre_parada']:
                QMessageBox.warning(self, "Error", "El nombre es obligatorio.")
                return
            db = SessionLocal()
            try:
                nueva = Parada(**data)
                db.add(nueva)
                db.commit()
                self.load_paradas()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo crear:\n{str(e)}")
            finally:
                db.close()

    def action_editar(self):
        selected = self.table.selectedItems()
        if not selected: return
        id_parada = int(self.table.item(selected[0].row(), 0).text())
        
        db = SessionLocal()
        try:
            parada = db.query(Parada).filter(Parada.id_parada == id_parada).first()
            if not parada: return
            
            dialog = ParadaDialog(self, parada=parada, id_ruta=parada.id_ruta)
            if dialog.exec():
                data = dialog.get_data()
                if not data['nombre_parada']:
                    QMessageBox.warning(self, "Error", "El nombre es obligatorio.")
                    return
                for key, val in data.items():
                    setattr(parada, key, val)
                db.commit()
                self.load_paradas()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo editar:\n{str(e)}")
        finally:
            db.close()

    def action_eliminar(self):
        selected = self.table.selectedItems()
        if not selected: return
        id_parada = int(self.table.item(selected[0].row(), 0).text())
        
        resp = QMessageBox.question(self, "Confirmar", "¿Eliminar esta parada?")
        if resp == QMessageBox.Yes:
            db = SessionLocal()
            try:
                parada = db.query(Parada).filter(Parada.id_parada == id_parada).first()
                if parada:
                    db.delete(parada)
                    db.commit()
                    self.load_paradas()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar:\n{str(e)}")
            finally:
                db.close()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CutGo - Desktop Admin")
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
        self.sidebar.setFixedWidth(220)
        
        items = [
            "📊 Dashboard", 
            "⏱️ Registro Horario", 
            "⚠️ Incidentes", 
            "🚌 Admin Rutas", 
            "📍 Admin Paradas"
        ]
        for item_text in items:
            item = QListWidgetItem(item_text)
            item.setSizeHint(QSize(200, 50))
            self.sidebar.addItem(item)
            
        self.sidebar.currentRowChanged.connect(self.change_view)
        main_layout.addWidget(self.sidebar)

        # --- Contenido Principal ---
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("mainContent")
        
        self.view_dashboard = DashboardView()
        self.view_horarios = RegistroHorarioView()
        self.view_incidentes = ReporteIncidenteView()
        self.view_admin_rutas = AdminRutasView()
        self.view_admin_paradas = AdminParadasView()

        self.stacked_widget.addWidget(self.view_dashboard)
        self.stacked_widget.addWidget(self.view_horarios)
        self.stacked_widget.addWidget(self.view_incidentes)
        self.stacked_widget.addWidget(self.view_admin_rutas)
        self.stacked_widget.addWidget(self.view_admin_paradas)

        main_layout.addWidget(self.stacked_widget)
        
        self.sidebar.setCurrentRow(0)
        self.apply_styles()

    def change_view(self, index):
        self.stacked_widget.setCurrentIndex(index)
        if index == 0:
            self.view_dashboard.load_data()
        elif index == 1:
            self.view_horarios.load_rutas()
            self.view_horarios.cb_ruta.setCurrentIndex(0)
        elif index == 2:
            self.view_incidentes.load_rutas()
            self.view_incidentes.cb_ruta.setCurrentIndex(0)
        elif index == 3:
            self.view_admin_rutas.load_data()
        elif index == 4:
            self.view_admin_paradas.load_rutas()

    def apply_styles(self):
        style_sheet = """
        QMainWindow { background-color: #121212; }
        QListWidget#sidebar {
            background-color: #1E1E24;
            color: #A0A0B5;
            border: none;
            border-right: 1px solid #2C2C35;
            font-size: 15px;
            font-weight: 600;
            padding-top: 20px;
        }
        QListWidget#sidebar::item { padding-left: 20px; border-radius: 8px; margin: 5px 10px; }
        QListWidget#sidebar::item:selected { background-color: #FF5E3A; color: white; }
        QListWidget#sidebar::item:hover:!selected { background-color: #2C2C35; color: white; }
        QWidget#mainContent { background-color: #121212; }
        QLabel { color: #FFFFFF; }
        QLabel#titleLabel { font-size: 28px; font-weight: 900; color: #FFFFFF; }
        QLabel#subtitleLabel { font-size: 14px; color: #8E8E9F; }
        QFrame#metricCard { background-color: #1E1E24; border-radius: 12px; padding: 20px; }
        QLabel#metricValue { font-size: 36px; font-weight: bold; color: #FFFFFF; }
        QLabel#metricTitle { font-size: 14px; color: #8E8E9F; font-weight: bold; margin-top: 5px; }
        QComboBox, QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QDateTimeEdit {
            background-color: #1E1E24; color: #FFFFFF; border: 1px solid #2C2C35;
            border-radius: 8px; padding: 10px; font-size: 14px;
        }
        QComboBox::drop-down { border: none; }
        QComboBox:disabled { background-color: #16161B; color: #55556A; }
        QPushButton {
            background-color: #2C2C35; color: white; border: none; border-radius: 8px;
            padding: 10px 15px; font-weight: bold; font-size: 14px;
        }
        QPushButton:hover { background-color: #3B3B46; }
        QPushButton#actionButton { background-color: #FF5E3A; border-radius: 25px; padding: 15px; }
        QPushButton#actionButton:hover { background-color: #FF7B5E; }
        QPushButton#dangerButton { background-color: #E74C3C; border-radius: 8px; padding: 10px; }
        QPushButton#dangerButton:hover { background-color: #F16051; }
        QTableWidget {
            background-color: #1E1E24; color: #FFFFFF; border: 1px solid #2C2C35;
            border-radius: 8px; gridline-color: #2C2C35;
        }
        QHeaderView::section { background-color: #2C2C35; color: #FFFFFF; font-weight: bold; border: none; padding: 8px; }
        QTableWidget::item:selected { background-color: #FF5E3A; color: white; }
        QCheckBox { color: white; font-size: 14px; }
        QDialog { background-color: #1E1E24; }
        """
        self.setStyleSheet(style_sheet)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())