# =============================================
# PUNTO DE ENTRADA DE LA APLICACIÓN
# =============================================
# Este archivo es el único que se ejecuta directamente.
# Su única responsabilidad es crear la aplicación Qt
# y mostrar la ventana principal.
#
# Uso: cd gui && python app.py
# =============================================

import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow


def main():
    # QApplication inicializa el entorno gráfico de Qt.
    # sys.argv permite pasar argumentos de línea de comandos a Qt si se necesitan.
    app = QApplication(sys.argv)

    # Crear y mostrar la ventana principal
    win = MainWindow()
    win.show()

    # app.exec() inicia el loop de eventos de Qt:
    # espera clics, teclado, señales y los procesa.
    # sys.exit() asegura que el código de salida se propague correctamente.
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
