import sys
from PySide6.QtWidgets import QApplication
from .window import MainWindow

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        if window is None:
            print("Error: Failed to initialize MainWindow")
        else:
            window.show()
            print("Entering application event loop")  # Debugging log
            sys.exit(app.exec())
    except Exception as e:
        print("An unexpected error occurred:", str(e))
        sys.exit(1)
