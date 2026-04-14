from typing import override
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QAction, QColor, QPainter, QPen, QKeyEvent
from PySide6.QtWidgets import QFileDialog, QMainWindow, QVBoxLayout, QWidget

from src.camera import Camera

from .modeler import EdgesIndices, VerticesArray, load_model


class ModelViewerWidget(QWidget):
    """A custom widget that renders 3D model using PySide6 QPainter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vertices: VerticesArray | None = None
        self.edges: EdgesIndices | None = None
        self.setGeometry(0, 0, 1024, 700)
        self.camera = None

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(16)

    @override
    def keyPressEvent(self, event: QKeyEvent, /) -> None:
        if not event.isAutoRepeat() and self.vertices is not None:
            self.camera.pressed_keys.add(event.key())

    @override
    def keyReleaseEvent(self, event: QKeyEvent, /) -> None:
        if not event.isAutoRepeat() and self.vertices is not None:
            self.camera.pressed_keys.discard(event.key())

    def update_scene(self):
        w = self.width()
        h = self.height()

        if self.vertices is not None:
            self.vertices = self.camera.update_state(w, h)
            self.update()

    def set_model(self, vertices: VerticesArray, edges: EdgesIndices) -> None:
        """Set the model data to be rendered."""
        self.vertices = vertices
        self.edges = edges
        self.update()
        self.camera = Camera(vertices)

    def paintEvent(self, event) -> None:
        """Paint the model using QPainter - draws from scratch on every update."""
        painter = QPainter(self)

        painter.fillRect(self.rect(), QColor(255, 255, 255))

        if self.vertices is not None and self.edges is not None:
            self._draw_edges(painter)

    def _draw_edges(self, painter: QPainter) -> None:
        """Draw edges on the painter with offset applied."""
        pen = QPen(QColor(255, 0, 0))  # Red color
        pen.setWidth(1)
        painter.setPen(pen)

        v = self.vertices.astype(int)

        for start, end in self.edges:
            painter.drawLine(v[start, 0], v[start, 1], v[end, 0], v[end, 1])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Model Viewer")
        self.setGeometry(100, 100, 1024, 768)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        self.model_viewer = ModelViewerWidget(self)
        layout.addWidget(self.model_viewer)
        layout.setContentsMargins(0, 0, 0, 0)

        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.load_action)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    @override
    def keyPressEvent(self, event: QKeyEvent, /) -> None:
        self.model_viewer.transform(event)

    def load_action(self):
        """
        Slot triggered when the Open File option is selected.
        Opens a dialog allowing the user to select a file.
        """
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Open File",
                "",
                "All Files (*);;Text Files (*.txt);;Model Files (*.obj *.ply)",
            )
            if file_path:
                print(f"File selected: {file_path}")
                with open(file_path, "r") as f:
                    vertices, edges = load_model(f)
                    self.model_viewer.set_model(vertices, edges)
                    self.model_viewer.update()
            else:
                print("No file was selected.")
        except Exception as e:
            print(f"An error occurred while loading a file: {e}")
