# =============================================
# FASE 4 — INTERFAZ GRÁFICA (PyQt6)
# =============================================
# PyQt6 es la librería de Python para crear
# ventanas, botones y tablas de escritorio.
#
# Estructura de la ventana:
#   ┌─────────────┬──────────────────────────┐
#   │   Sidebar   │   Área de contenido      │
#   │  (menú de   │   (cambia según la       │
#   │  navegación)│    sección activa)        │
#   └─────────────┴──────────────────────────┘
#
# El área de contenido usa QStackedWidget:
# apila todas las páginas encima de sí mismas
# y muestra solo la que corresponde al botón
# presionado en el sidebar.
# =============================================

import sys
import os
import json
import subprocess

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QLineEdit,
    QStackedWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QProgressBar, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor

# Permite importar config.py desde la carpeta etl/ sin estar en ese directorio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "etl"))
from config import POSTGRES_CONFIG, MONGO_URI, MONGO_DB, REDIS_HOST, REDIS_PORT

# ─────────────────────────────────────────────
# PALETA DE COLORES — Catppuccin Mocha
# Tema oscuro con colores pastel definidos como
# constantes hexadecimales. Usarlos desde el
# diccionario C evita escribir el código de color
# repetido y hace fácil cambiar el tema completo.
# ─────────────────────────────────────────────
C = {
    "base":    "#1e1e2e",
    "mantle":  "#181825",
    "crust":   "#11111b",
    "surf0":   "#313244",
    "surf1":   "#45475a",
    "surf2":   "#585b70",
    "text":    "#cdd6f4",
    "sub0":    "#a6adc8",
    "blue":    "#89b4fa",
    "green":   "#a6e3a1",
    "red":     "#f38ba8",
    "yellow":  "#f9e2af",
    "peach":   "#fab387",
    "mauve":   "#cba6f7",
    "teal":    "#94e2d5",
    "lavender":"#b4befe",
}

QSS = f"""
* {{
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
    color: {C['text']};
}}
QMainWindow, QWidget {{ background-color: {C['base']}; }}

/* ── Sidebar ── */
#sidebar {{
    background-color: {C['mantle']};
    border-right: 1px solid {C['surf0']};
    min-width: 230px;
    max-width: 230px;
}}
#app-title {{
    font-size: 17px;
    font-weight: bold;
    color: {C['lavender']};
    padding: 22px 18px 4px 18px;
}}
#app-sub {{
    font-size: 11px;
    color: {C['sub0']};
    padding: 0 18px 18px 18px;
}}

/* ── Botones nav ── */
#nav-btn {{
    background: transparent;
    border: none;
    text-align: left;
    padding: 11px 18px;
    border-radius: 8px;
    margin: 2px 8px;
    font-size: 13px;
    color: {C['sub0']};
}}
#nav-btn:hover {{ background: {C['surf0']}; color: {C['text']}; }}
#nav-btn[active=true] {{
    background: {C['surf0']};
    color: {C['blue']};
    font-weight: bold;
    border-left: 3px solid {C['blue']};
    padding-left: 15px;
}}

/* ── Botón acción ── */
#action-btn {{
    background: {C['blue']};
    color: {C['crust']};
    font-weight: bold;
    padding: 9px 22px;
    border: none;
    border-radius: 8px;
}}
#action-btn:hover {{ background: {C['lavender']}; }}
#action-btn:disabled {{ background: {C['surf1']}; color: {C['sub0']}; }}

/* ── Log / terminal ── */
#log-area {{
    background: {C['crust']};
    color: {C['green']};
    border: 1px solid {C['surf1']};
    border-radius: 8px;
    padding: 8px;
    font-family: 'Cascadia Code', Consolas, 'Courier New', monospace;
    font-size: 12px;
}}

/* ── Tabla ── */
QTableWidget {{
    background: {C['crust']};
    border: 1px solid {C['surf1']};
    border-radius: 8px;
    gridline-color: {C['surf0']};
    alternate-background-color: {C['surf0']};
    selection-background-color: {C['surf1']};
}}
QTableWidget::item {{ padding: 5px 10px; }}
QHeaderView::section {{
    background: {C['surf1']};
    color: {C['lavender']};
    font-weight: bold;
    padding: 7px 10px;
    border: none;
    border-right: 1px solid {C['surf0']};
    border-bottom: 1px solid {C['surf0']};
}}

/* ── Input ── */
QLineEdit {{
    background: {C['surf0']};
    border: 1px solid {C['surf1']};
    border-radius: 6px;
    padding: 7px 12px;
    color: {C['text']};
}}
QLineEdit:focus {{ border: 1px solid {C['blue']}; }}

/* ── Progress bar ── */
QProgressBar {{
    background: {C['surf0']};
    border: none;
    border-radius: 3px;
    height: 5px;
}}
QProgressBar::chunk {{ background: {C['blue']}; border-radius: 3px; }}

/* ── Status bar ── */
QStatusBar {{
    background: {C['mantle']};
    border-top: 1px solid {C['surf0']};
    color: {C['sub0']};
    font-size: 11px;
    padding: 2px 8px;
}}

/* ── Scroll ── */
QScrollBar:vertical {{
    background: {C['surf0']};
    width: 7px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {C['surf2']};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
"""


# ─────────────────────────────────────────────
# WORKER THREAD — ETL sin bloquear la pantalla
# ─────────────────────────────────────────────
# Problema: si corremos el ETL directamente en la GUI,
# Python ejecuta una cosa a la vez → la ventana se congela
# hasta que el ETL termine (puede tardar 2-3 minutos con Cassandra).
#
# Solución: QThread crea un hilo paralelo.
# El ETL corre en ese hilo; la GUI sigue viva en el hilo principal.
#
# Comunicación entre hilos:
#   pyqtSignal(str) → emite una señal cada vez que el ETL imprime una línea.
#   pyqtSignal(bool) → emite True/False cuando el ETL termina (éxito/error).
#   La GUI se suscribe a estas señales y actualiza la pantalla al recibirlas.
# ─────────────────────────────────────────────
class EtlWorker(QThread):
    log_line = pyqtSignal(str)   # señal: nueva línea de log disponible
    finished = pyqtSignal(bool)  # señal: ETL terminó (True=OK, False=error)

    def run(self):
        etl_script = os.path.join(os.path.dirname(__file__), "..", "etl", "run_etl.py")

        # subprocess.Popen lanza run_etl.py como un proceso hijo separado.
        # PYTHONUTF8=1 fuerza UTF-8 en ese proceso para que las tildes
        # no generen UnicodeEncodeError en la consola de Windows.
        # stderr=STDOUT redirige los errores al mismo canal que la salida normal.
        proc = subprocess.Popen(
            [sys.executable, "-u", etl_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env={**os.environ, "PYTHONUTF8": "1"},
        )

        # Leer la salida línea por línea en tiempo real.
        # Cada línea se emite como señal → la GUI la agrega al log inmediatamente.
        for raw in proc.stdout:
            self.log_line.emit(raw.decode("utf-8", errors="replace").rstrip())

        proc.wait()
        # returncode == 0 significa que el proceso terminó sin errores
        self.finished.emit(proc.returncode == 0)


# ─────────────────────────────────────────────
# FUNCIONES AUXILIARES (helpers)
# Pequeñas funciones reutilizables para no
# repetir el mismo código en cada sección.
# ─────────────────────────────────────────────

def sep() -> QFrame:
    """Crea una línea horizontal de separación visual."""
    f = QFrame()
    f.setFixedHeight(1)
    f.setStyleSheet(f"background: {C['surf1']}; border: none;")
    return f


def badge(text: str, color: str) -> QLabel:
    """
    Crea una etiqueta con fondo de color suave y borde redondeado.
    Se usa para mostrar el estado de cada paso del ETL (gris=pendiente, verde=listo).
    """
    lbl = QLabel(text)
    lbl.setStyleSheet(f"""
        background: {color}22;
        color: {color};
        border: 1px solid {color}88;
        border-radius: 10px;
        padding: 2px 12px;
        font-size: 11px;
        font-weight: bold;
    """)
    lbl.setFixedHeight(22)
    return lbl


def fill_table(tbl: QTableWidget, rows: list) -> None:
    """
    Rellena un QTableWidget con una lista de diccionarios.
    Detecta automáticamente las columnas del primer diccionario.
    Hace las celdas de solo lectura para que el usuario no pueda editarlas.
    """
    if not rows:
        tbl.setRowCount(0)
        return
    cols = list(rows[0].keys())          # nombres de columnas del primer dict
    tbl.setColumnCount(len(cols))
    tbl.setHorizontalHeaderLabels(cols)
    tbl.setRowCount(len(rows))
    for r, row in enumerate(rows):
        for c, col in enumerate(cols):
            item = QTableWidgetItem(str(row[col]) if row[col] is not None else "")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # solo lectura
            tbl.setItem(r, c, item)
    tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    tbl.setAlternatingRowColors(True)
    tbl.verticalHeader().setVisible(False)


def action_btn(text: str) -> QPushButton:
    """Crea un botón con el estilo de acción principal definido en el QSS."""
    btn = QPushButton(text)
    btn.setObjectName("action-btn")
    btn.setFixedHeight(38)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn


# ──────────────────────────────────────────────────────────────────────────────
# VENTANA PRINCIPAL
# ──────────────────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Red Social Académica — BD2 Final")
        self.resize(1250, 780)
        self.setMinimumSize(960, 620)
        self.setStyleSheet(QSS)

        central = QWidget()
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setCentralWidget(central)

        # ── Sidebar ──────────────────────────────────────────────────────────
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sb_lay = QVBoxLayout(sidebar)
        sb_lay.setContentsMargins(0, 0, 0, 16)
        sb_lay.setSpacing(0)

        title = QLabel("🎓 Red Social")
        title.setObjectName("app-title")
        sub   = QLabel("BD2 · Persistencia Políglota")
        sub.setObjectName("app-sub")
        sb_lay.addWidget(title)
        sb_lay.addWidget(sub)
        sb_lay.addWidget(sep())

        self._stack = QStackedWidget()
        nav_items = [
            ("⚡  ETL Políglota",        self._page_etl()),
            ("🐘  PostgreSQL",           self._page_postgres()),
            ("🍃  MongoDB",              self._page_mongo()),
            ("💿  Cassandra",            self._page_cassandra()),
            ("🔴  Redis",                self._page_redis()),
            ("🔗  Procedimientos",       self._page_procedimientos()),
        ]

        self._nav_btns: list[QPushButton] = []
        for i, (label, page) in enumerate(nav_items):
            btn = QPushButton(label)
            btn.setObjectName("nav-btn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=i: self._nav(idx))
            sb_lay.addWidget(btn)
            self._stack.addWidget(page)
            self._nav_btns.append(btn)

        sb_lay.addStretch()
        sb_lay.addWidget(sep())

        # Indicadores de conexión al pie del sidebar
        conn_lbl = QLabel("  Conexiones")
        conn_lbl.setStyleSheet(f"color:{C['sub0']}; font-size:11px; padding:8px 16px 4px;")
        sb_lay.addWidget(conn_lbl)
        for name, color in [("PostgreSQL",C["green"]),("MongoDB",C["green"]),
                             ("Cassandra",C["yellow"]),("Redis",C["green"])]:
            row = QWidget()
            rl  = QHBoxLayout(row)
            rl.setContentsMargins(16, 2, 16, 2)
            dot = QLabel("●")
            dot.setStyleSheet(f"color:{color}; font-size:9px;")
            lbl = QLabel(name)
            lbl.setStyleSheet(f"color:{C['sub0']}; font-size:11px;")
            rl.addWidget(dot); rl.addWidget(lbl); rl.addStretch()
            sb_lay.addWidget(row)

        root.addWidget(sidebar)
        root.addWidget(self._stack, 1)
        self.statusBar().showMessage("Listo · Ejecuta el ETL para empezar")
        self._nav(0)

    # ── Navegación ────────────────────────────────────────────────────────────
    def _nav(self, idx: int) -> None:
        for i, btn in enumerate(self._nav_btns):
            btn.setProperty("active", "true" if i == idx else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self._stack.setCurrentIndex(idx)

    # ── Contenedor de página ──────────────────────────────────────────────────
    def _page(self, title: str, subtitle: str) -> tuple:
        w   = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(36, 28, 36, 28)
        lay.setSpacing(10)
        t = QLabel(title)
        t.setStyleSheet(f"font-size:20px; font-weight:bold; color:{C['text']};")
        s = QLabel(subtitle)
        s.setStyleSheet(f"font-size:12px; color:{C['sub0']}; margin-bottom:4px;")
        lay.addWidget(t)
        lay.addWidget(s)
        lay.addWidget(sep())
        return w, lay

    # ─────────────────────────────────────────────────────────────────────────
    # PÁGINA ETL
    # ─────────────────────────────────────────────────────────────────────────
    def _page_etl(self) -> QWidget:
        w, lay = self._page(
            "⚡ ETL Políglota",
            "Extrae datos de PostgreSQL y los migra a MongoDB, Cassandra y Redis en un solo clic."
        )

        # Botón principal
        btn_row = QHBoxLayout()
        self._etl_btn = action_btn("▶  Ejecutar ETL Completo")
        self._etl_btn.setFixedHeight(44)
        self._etl_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {C['blue']}, stop:1 {C['mauve']});
                color: {C['crust']};
                font-weight: bold;
                font-size: 14px;
                padding: 10px 28px;
                border: none;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {C['lavender']}, stop:1 {C['blue']});
            }}
            QPushButton:disabled {{
                background: {C['surf1']};
                color: {C['sub0']};
            }}
        """)
        self._etl_btn.clicked.connect(self._run_etl)
        btn_row.addWidget(self._etl_btn)
        btn_row.addStretch()
        lay.addLayout(btn_row)

        # Progress bar
        self._etl_bar = QProgressBar()
        self._etl_bar.setFixedHeight(5)
        self._etl_bar.setTextVisible(False)
        self._etl_bar.hide()
        lay.addWidget(self._etl_bar)

        # Badges de pasos
        brow = QHBoxLayout()
        self._b_pg = badge("1 · PostgreSQL", C["sub0"])
        self._b_mg = badge("2 · MongoDB",    C["sub0"])
        self._b_ca = badge("3 · Cassandra",  C["sub0"])
        self._b_re = badge("4 · Redis",      C["sub0"])
        for b in [self._b_pg, self._b_mg, self._b_ca, self._b_re]:
            brow.addWidget(b)
        brow.addStretch()
        lay.addLayout(brow)

        # Log
        log_hdr = QLabel("Log de ejecución")
        log_hdr.setStyleSheet(f"color:{C['sub0']}; font-size:11px; margin-top:6px;")
        lay.addWidget(log_hdr)

        self._etl_log = QTextEdit()
        self._etl_log.setObjectName("log-area")
        self._etl_log.setReadOnly(True)
        self._etl_log.setPlaceholderText("El log aparecerá aquí al ejecutar el ETL...")
        lay.addWidget(self._etl_log)
        return w

    def _run_etl(self):
        self._etl_log.clear()
        self._etl_btn.setEnabled(False)
        self._etl_bar.setRange(0, 0)
        self._etl_bar.show()
        self.statusBar().showMessage("Ejecutando ETL...")
        for b, name, num in [
            (self._b_pg, "PostgreSQL", "1"),
            (self._b_mg, "MongoDB",    "2"),
            (self._b_ca, "Cassandra",  "3"),
            (self._b_re, "Redis",      "4"),
        ]:
            b.setText(f"{num} · {name}")
            b.setStyleSheet(f"background:{C['surf0']}44; color:{C['sub0']}; border:1px solid {C['surf1']}; border-radius:10px; padding:2px 12px; font-size:11px; font-weight:bold;")

        self._worker = EtlWorker()
        self._worker.log_line.connect(self._etl_line)
        self._worker.finished.connect(self._etl_done)
        self._worker.start()

    def _etl_line(self, line: str):
        def colored(text, color, bold=False):
            weight = "bold" if bold else "normal"
            return f'<span style="color:{color};font-weight:{weight};">{text}</span>'

        if not line.strip():
            self._etl_log.append("")
            return

        if any(k in line for k in ("Error", "ERROR", "Traceback", "failed")):
            self._etl_log.append(colored(line, C["red"]))
        elif "===" in line:
            self._etl_log.append(colored(line, C["mauve"], bold=True))
        elif "[1/4]" in line or ("[MongoDB]" not in line and "PostgreSQL" in line and "extraí" in line):
            self._etl_log.append(colored(line, C["blue"]))
            if "extraí" in line:
                self._set_badge(self._b_pg, "✓ PostgreSQL", C["green"])
        elif "[2/4]" in line:
            self._etl_log.append(colored(line, C["teal"]))
        elif "[MongoDB]" in line:
            self._etl_log.append(colored(line, C["green"]))
            self._set_badge(self._b_mg, "✓ MongoDB", C["green"])
        elif "[3/4]" in line:
            self._etl_log.append(colored(line, C["yellow"]))
        elif "[Cassandra]" in line:
            self._etl_log.append(colored(line, C["yellow"]))
            if "insertadas" in line:
                self._set_badge(self._b_ca, "✓ Cassandra", C["green"])
        elif "[4/4]" in line:
            self._etl_log.append(colored(line, C["peach"]))
        elif "[Redis]" in line:
            self._etl_log.append(colored(line, C["peach"]))
            self._set_badge(self._b_re, "✓ Redis", C["green"])
        else:
            self._etl_log.append(colored(line, C["text"]))

    def _set_badge(self, b: QLabel, text: str, color: str):
        b.setText(text)
        b.setStyleSheet(f"background:{color}22; color:{color}; border:1px solid {color}88; border-radius:10px; padding:2px 12px; font-size:11px; font-weight:bold;")

    def _etl_done(self, ok: bool):
        self._etl_btn.setEnabled(True)
        self._etl_bar.hide()
        if ok:
            self._etl_log.append(f'<br><b><span style="color:{C["green"]}">✓ ETL completado exitosamente.</span></b>')
            self.statusBar().showMessage("✓ ETL completado.", 6000)
        else:
            self._etl_log.append(f'<br><b><span style="color:{C["red"]}">✗ ETL falló — revisa el log.</span></b>')
            self.statusBar().showMessage("✗ ETL falló.", 6000)

    # ─────────────────────────────────────────────────────────────────────────
    # PÁGINA POSTGRESQL
    # ─────────────────────────────────────────────────────────────────────────
    def _page_postgres(self) -> QWidget:
        w, lay = self._page(
            "🐘 PostgreSQL",
            "Consulta la tabla de usuarios o la vista feed_noticias directamente desde PostgreSQL."
        )
        btn_usuarios = action_btn("👥  Ver Usuarios (50)")
        btn_usuarios.clicked.connect(self._load_pg_usuarios)
        btn_feed = action_btn("📰  Ver feed_noticias")
        btn_feed.clicked.connect(self._load_pg_feed)
        row = QHBoxLayout()
        row.addWidget(btn_usuarios)
        row.addSpacing(8)
        row.addWidget(btn_feed)
        row.addStretch()
        lay.addLayout(row)
        self._pg_table = QTableWidget()
        lay.addWidget(self._pg_table)
        return w

    def _load_pg_usuarios(self):
        """
        Consulta la tabla 'usuarios' directamente y muestra los 50 registros.
        Demuestra que el Excel fue cargado correctamente en PostgreSQL.
        """
        try:
            import psycopg2, psycopg2.extras
            conn = psycopg2.connect(**POSTGRES_CONFIG)
            cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT id_usuario, nombre, email, fecha_registro, pais FROM usuarios ORDER BY id_usuario;")
            rows = [dict(r) for r in cur.fetchall()]
            cur.close(); conn.close()
            fill_table(self._pg_table, rows)
            self.statusBar().showMessage(f"PostgreSQL · {len(rows)} usuarios cargados.", 5000)
        except Exception as e:
            self.statusBar().showMessage(f"Error PostgreSQL: {e}", 7000)

    def _load_pg_feed(self):
        """
        Ejecuta SELECT * FROM feed_noticias (la vista creada en Fase 2).
        Muestra publicaciones con su autor y el conteo de comentarios ya calculado.
        """
        try:
            import psycopg2, psycopg2.extras
            conn = psycopg2.connect(**POSTGRES_CONFIG)
            cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT * FROM feed_noticias;")
            rows = [dict(r) for r in cur.fetchall()]
            cur.close(); conn.close()
            fill_table(self._pg_table, rows)
            self.statusBar().showMessage(f"PostgreSQL · {len(rows)} publicaciones en feed.", 5000)
        except Exception as e:
            self.statusBar().showMessage(f"Error PostgreSQL: {e}", 7000)

    # ─────────────────────────────────────────────────────────────────────────
    # PÁGINA MONGODB
    # ─────────────────────────────────────────────────────────────────────────
    def _page_mongo(self) -> QWidget:
        w, lay = self._page(
            "🍃 MongoDB",
            "Publicaciones con autor embebido y array de comentarios (documento enriquecido)."
        )
        btn = action_btn("🔄  Cargar publicaciones")
        btn.clicked.connect(self._load_mongo)
        row = QHBoxLayout()
        row.addWidget(btn); row.addStretch()
        lay.addLayout(row)
        self._mongo_out = QTextEdit()
        self._mongo_out.setObjectName("log-area")
        self._mongo_out.setReadOnly(True)
        self._mongo_out.setFont(QFont("Cascadia Code, Consolas", 11))
        lay.addWidget(self._mongo_out)
        return w

    def _load_mongo(self):
        """
        Lee los primeros 10 documentos de la colección 'publicaciones' en MongoDB
        y los muestra como JSON con colores (syntax highlighting manual).
        Cada documento tiene el autor embebido y el arreglo de comentarios adentro.
        El límite de 10 es para no saturar la pantalla; en producción se paginaría.
        """
        try:
            from pymongo import MongoClient
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
            docs   = list(client[MONGO_DB].publicaciones.find().limit(10))
            client.close()
            self._mongo_out.clear()
            for d in docs:
                d.pop("_id", None)  # ocultar el _id interno de MongoDB
                self._mongo_out.append(self._json_html(json.dumps(d, ensure_ascii=False, indent=2, default=str)))
                self._mongo_out.append(f'<span style="color:{C["surf2"]};">{"─" * 48}</span>')
            self.statusBar().showMessage(f"MongoDB · {len(docs)} documentos cargados.", 5000)
        except Exception as e:
            self._mongo_out.setText(f"Error: {e}")

    def _json_html(self, text: str) -> str:
        lines = []
        for line in text.split("\n"):
            if '": ' in line:
                key, _, val = line.partition('": ')
                kp = f'<span style="color:{C["blue"]}">{key}"</span>: '
                if val.startswith('"'):
                    vp = f'<span style="color:{C["green"]}">{val}</span>'
                elif val.strip().rstrip(",") in ("true","false","null"):
                    vp = f'<span style="color:{C["peach"]}">{val}</span>'
                elif val.strip().rstrip(",").lstrip("-").isdigit():
                    vp = f'<span style="color:{C["mauve"]}">{val}</span>'
                else:
                    vp = f'<span style="color:{C["text"]}">{val}</span>'
                lines.append(kp + vp)
            elif line.strip() in ("{", "}", "[", "]", "},", "],"):
                lines.append(f'<span style="color:{C["sub0"]}">{line}</span>')
            else:
                lines.append(f'<span style="color:{C["text"]}">{line}</span>')
        return "<br>".join(lines)

    # ─────────────────────────────────────────────────────────────────────────
    # PÁGINA CASSANDRA
    # ─────────────────────────────────────────────────────────────────────────
    def _page_cassandra(self) -> QWidget:
        w, lay = self._page(
            "💿 Cassandra",
            "Timeline de un usuario — publicaciones ordenadas por fecha descendente (partition key: usuario_id)."
        )
        input_row = QHBoxLayout()
        self._cass_uid = QLineEdit()
        self._cass_uid.setPlaceholderText("ID de usuario (ej: 1)")
        self._cass_uid.setFixedWidth(200)
        self._cass_uid.returnPressed.connect(self._load_cassandra)
        btn = action_btn("🔄  Ver Timeline")
        btn.clicked.connect(self._load_cassandra)
        lbl = QLabel("Usuario:")
        lbl.setStyleSheet(f"color:{C['sub0']};")
        input_row.addWidget(lbl)
        input_row.addWidget(self._cass_uid)
        input_row.addSpacing(8)
        input_row.addWidget(btn)
        input_row.addStretch()
        lay.addLayout(input_row)
        self._cass_table = QTableWidget()
        lay.addWidget(self._cass_table)
        return w

    def _load_cassandra(self):
        """
        Consulta el timeline de un usuario específico en Cassandra.
        Gracias al diseño del schema (partition key = usuario_id),
        Cassandra va directo a la partición del usuario pedido
        sin escanear toda la tabla.
        Los resultados llegan ya ordenados por fecha DESC
        sin necesitar ORDER BY (lo garantiza CLUSTERING ORDER BY).
        """
        try:
            from cassandra.cluster import Cluster
            from cassandra.policies import DCAwareRoundRobinPolicy
            uid     = int(self._cass_uid.text() or "1")
            cluster = Cluster(["localhost"],
                              load_balancing_policy=DCAwareRoundRobinPolicy(local_dc="datacenter1"),
                              connect_timeout=10)
            session = cluster.connect("red_social")

            # WHERE usuario_id = ? aprovecha la partition key → lectura eficiente
            rows = list(session.execute(
                "SELECT * FROM timeline_usuarios WHERE usuario_id=%s LIMIT 20", [uid]
            ))
            cluster.shutdown()

            if rows:
                # Las filas de Cassandra son namedtuples; _fields da los nombres de columna
                cols = rows[0]._fields
                fill_table(self._cass_table, [{c: getattr(r, c) for c in cols} for r in rows])
                self.statusBar().showMessage(f"Cassandra · {len(rows)} filas para usuario {uid}.", 5000)
            else:
                self._cass_table.setRowCount(0)
                self.statusBar().showMessage("Cassandra · sin datos para ese usuario.", 5000)
        except Exception as e:
            self.statusBar().showMessage(f"Error Cassandra: {e}", 7000)

    # ─────────────────────────────────────────────────────────────────────────
    # PÁGINA REDIS
    # ─────────────────────────────────────────────────────────────────────────
    def _page_redis(self) -> QWidget:
        w, lay = self._page(
            "🔴 Redis",
            "Claves activas en caché: feed de noticias, likes por publicación y total de usuarios (TTL 5 min)."
        )
        btn = action_btn("🔄  Leer caché")
        btn.clicked.connect(self._load_redis)
        row = QHBoxLayout()
        row.addWidget(btn); row.addStretch()
        lay.addLayout(row)

        self._redis_table = QTableWidget()
        self._redis_table.setColumnCount(3)
        self._redis_table.setHorizontalHeaderLabels(["Clave", "Valor", "TTL (s)"])
        hdr = self._redis_table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._redis_table.setAlternatingRowColors(True)
        self._redis_table.verticalHeader().setVisible(False)
        lay.addWidget(self._redis_table)
        return w

    def _load_redis(self):
        try:
            import redis as redis_lib
            r    = redis_lib.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
            keys = sorted(r.keys("*"))
            self._redis_table.setRowCount(len(keys))
            for i, key in enumerate(keys):
                val = r.get(key) or ""
                ttl = str(r.ttl(key))
                if key == "cache:feed_noticias":
                    val = f"[JSON · {len(val)} chars]"
                k_item = QTableWidgetItem(key)
                k_item.setForeground(QColor(C["blue"]))
                k_item.setFlags(k_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                v_item = QTableWidgetItem(val)
                v_item.setFlags(v_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                t_item = QTableWidgetItem(ttl)
                t_item.setForeground(QColor(C["yellow"]))
                t_item.setFlags(t_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self._redis_table.setItem(i, 0, k_item)
                self._redis_table.setItem(i, 1, v_item)
                self._redis_table.setItem(i, 2, t_item)
            self.statusBar().showMessage(f"Redis · {len(keys)} claves en caché.", 5000)
        except Exception as e:
            self.statusBar().showMessage(f"Error Redis: {e}", 7000)

    # ─────────────────────────────────────────────────────────────────────────
    # PÁGINA PROCEDIMIENTOS
    # ─────────────────────────────────────────────────────────────────────────
    def _page_procedimientos(self) -> QWidget:
        w, lay = self._page(
            "🔗 Procedimientos Almacenados",
            "Ejecuta CALL crear_amistad y CALL aceptar_amistad para gestionar el ciclo completo."
        )

        # ── Card: Crear solicitud ─────────────────────────────────────
        card = QFrame()
        card.setStyleSheet(f"background:{C['surf0']}; border-radius:12px;")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(24, 18, 24, 18)
        card_lay.setSpacing(12)

        hdr = QLabel("Crear solicitud de amistad")
        hdr.setStyleSheet(f"font-size:14px; font-weight:bold; color:{C['lavender']};")
        card_lay.addWidget(hdr)

        form = QHBoxLayout()
        for attr, ph, lbl_txt in [
            ("_proc_id1", "ej: 1", "Usuario 1:"),
            ("_proc_id2", "ej: 5", "Usuario 2:"),
        ]:
            lbl = QLabel(lbl_txt)
            lbl.setStyleSheet(f"color:{C['sub0']};")
            inp = QLineEdit()
            inp.setPlaceholderText(ph)
            inp.setFixedWidth(110)
            setattr(self, attr, inp)
            form.addWidget(lbl)
            form.addWidget(inp)
            form.addSpacing(12)

        btn_friend = QPushButton("🔗  Crear Amistad")
        btn_friend.setFixedHeight(38)
        btn_friend.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_friend.setStyleSheet(f"""
            QPushButton {{
                background: {C['mauve']};
                color: {C['crust']};
                font-weight: bold;
                padding: 8px 20px;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{ background: {C['lavender']}; }}
        """)
        btn_friend.clicked.connect(self._call_procedure)
        form.addWidget(btn_friend)
        form.addStretch()
        card_lay.addLayout(form)

        self._proc_out = QTextEdit()
        self._proc_out.setObjectName("log-area")
        self._proc_out.setReadOnly(True)
        self._proc_out.setFixedHeight(60)
        self._proc_out.setPlaceholderText("Resultado del procedimiento...")
        card_lay.addWidget(self._proc_out)
        lay.addWidget(card)

        lay.addSpacing(8)

        # ── Card: Aceptar solicitud ───────────────────────────────────
        card2 = QFrame()
        card2.setStyleSheet(f"background:{C['surf0']}; border-radius:12px;")
        card2_lay = QVBoxLayout(card2)
        card2_lay.setContentsMargins(24, 18, 24, 18)
        card2_lay.setSpacing(12)

        hdr2 = QLabel("Aceptar solicitud de amistad")
        hdr2.setStyleSheet(f"font-size:14px; font-weight:bold; color:{C['green']};")
        card2_lay.addWidget(hdr2)

        desc2 = QLabel("Cambia una solicitud PENDIENTE a ACEPTADA — pasa de solicitudes pendientes a amistades consolidadas.")
        desc2.setStyleSheet(f"font-size:12px; color:{C['sub0']};")
        desc2.setWordWrap(True)
        card2_lay.addWidget(desc2)

        form2 = QHBoxLayout()
        for attr, ph, lbl_txt in [
            ("_acep_id1", "ej: 1", "Usuario 1:"),
            ("_acep_id2", "ej: 5", "Usuario 2:"),
        ]:
            lbl = QLabel(lbl_txt)
            lbl.setStyleSheet(f"color:{C['sub0']};")
            inp = QLineEdit()
            inp.setPlaceholderText(ph)
            inp.setFixedWidth(110)
            setattr(self, attr, inp)
            form2.addWidget(lbl)
            form2.addWidget(inp)
            form2.addSpacing(12)

        btn_acept = QPushButton("✅  Aceptar Amistad")
        btn_acept.setFixedHeight(38)
        btn_acept.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_acept.setStyleSheet(f"""
            QPushButton {{
                background: {C['green']};
                color: {C['crust']};
                font-weight: bold;
                padding: 8px 20px;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{ background: {C['teal']}; }}
        """)
        btn_acept.clicked.connect(self._accept_procedure)
        form2.addWidget(btn_acept)
        form2.addStretch()
        card2_lay.addLayout(form2)

        self._acep_out = QTextEdit()
        self._acep_out.setObjectName("log-area")
        self._acep_out.setReadOnly(True)
        self._acep_out.setFixedHeight(60)
        self._acep_out.setPlaceholderText("Resultado del procedimiento...")
        card2_lay.addWidget(self._acep_out)
        lay.addWidget(card2)

        # ── Vistas de amistades ───────────────────────────────────────
        lay.addSpacing(6)
        views_title = QLabel("Vistas de amistades")
        views_title.setStyleSheet(f"font-size:15px; font-weight:bold; color:{C['text']};")
        lay.addWidget(views_title)

        views_row = QHBoxLayout()
        btn_pend = QPushButton("📋  Solicitudes Pendientes")
        btn_pend.setFixedHeight(36)
        btn_pend.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pend.setStyleSheet(f"background:{C['yellow']}; color:{C['crust']}; font-weight:bold; padding:8px 16px; border:none; border-radius:8px;")
        btn_pend.clicked.connect(lambda: self._load_view("solicitudes_pendientes"))

        btn_acep = QPushButton("✅  Amistades Consolidadas")
        btn_acep.setFixedHeight(36)
        btn_acep.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_acep.setStyleSheet(f"background:{C['green']}; color:{C['crust']}; font-weight:bold; padding:8px 16px; border:none; border-radius:8px;")
        btn_acep.clicked.connect(lambda: self._load_view("amistades_consolidadas"))

        views_row.addWidget(btn_pend)
        views_row.addWidget(btn_acep)
        views_row.addStretch()
        lay.addLayout(views_row)

        self._view_table = QTableWidget()
        lay.addWidget(self._view_table)
        return w

    def _call_procedure(self):
        """
        Ejecuta el stored procedure crear_amistad(id1, id2) en PostgreSQL.

        autocommit = True es necesario para que PostgreSQL envíe los RAISE NOTICE
        de vuelta a Python. Sin autocommit, los notices quedan en buffer y nunca llegan.

        conn.notices es una lista donde PostgreSQL deposita todos los mensajes NOTICE
        generados durante la sesión. El procedimiento pone ahí el resultado.

        Verde = amistad creada. Amarillo = ya existía.
        """
        try:
            import psycopg2
            id1  = int(self._proc_id1.text())
            id2  = int(self._proc_id2.text())
            conn = psycopg2.connect(**POSTGRES_CONFIG)
            conn.autocommit = True  # necesario para recibir los RAISE NOTICE
            cur  = conn.cursor()
            cur.execute("CALL crear_amistad(%s, %s)", (id1, id2))
            notices = list(conn.notices)  # leer los mensajes del procedimiento
            cur.close(); conn.close()
            self._proc_out.clear()
            for n in notices:
                msg = n.strip()
                if "creada" in msg:
                    self._proc_out.append(f'<span style="color:{C["green"]}">✓ {msg}</span>')
                else:
                    self._proc_out.append(f'<span style="color:{C["yellow"]}">⚠ {msg}</span>')
            self.statusBar().showMessage("Procedimiento ejecutado.", 5000)
        except Exception as e:
            self._proc_out.setHtml(f'<span style="color:{C["red"]}">✗ Error: {e}</span>')

    def _accept_procedure(self):
        """
        Ejecuta CALL aceptar_amistad(id1, id2).
        Cambia el estado de PENDIENTE a ACEPTADA usando UPDATE en el procedimiento.
        Después de aceptar, la fila desaparece de solicitudes_pendientes
        y aparece en amistades_consolidadas.
        """
        try:
            import psycopg2
            id1  = int(self._acep_id1.text())
            id2  = int(self._acep_id2.text())
            conn = psycopg2.connect(**POSTGRES_CONFIG)
            conn.autocommit = True
            cur  = conn.cursor()
            cur.execute("CALL aceptar_amistad(%s, %s)", (id1, id2))
            notices = list(conn.notices)
            cur.close(); conn.close()
            self._acep_out.clear()
            for n in notices:
                msg = n.strip()
                if "exitosamente" in msg:
                    self._acep_out.append(f'<span style="color:{C["green"]}">✓ {msg}</span>')
                else:
                    self._acep_out.append(f'<span style="color:{C["yellow"]}">⚠ {msg}</span>')
            self.statusBar().showMessage("Procedimiento ejecutado.", 5000)
        except Exception as e:
            self._acep_out.setHtml(f'<span style="color:{C["red"]}">✗ Error: {e}</span>')

    def _load_view(self, view: str):
        try:
            import psycopg2, psycopg2.extras
            conn = psycopg2.connect(**POSTGRES_CONFIG)
            cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(f"SELECT * FROM {view};")
            rows = [dict(r) for r in cur.fetchall()]
            cur.close(); conn.close()
            fill_table(self._view_table, rows)
            self.statusBar().showMessage(f"{view} · {len(rows)} filas.", 5000)
        except Exception as e:
            self.statusBar().showMessage(f"Error: {e}", 7000)
