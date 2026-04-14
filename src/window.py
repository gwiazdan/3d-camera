from typing import override
from typing import IO

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QAction, QColor, QKeyEvent, QPainter, QPen
from PySide6.QtWidgets import QFileDialog, QMainWindow, QVBoxLayout, QWidget
import numpy as np
import numpy.typing as npt

VerticesArray = npt.NDArray[np.float32]
EdgesIndices = npt.NDArray[np.int16]

from src.camera import Camera


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
                    vertices, edges = self.load_model(f)
                    self.model_viewer.set_model(vertices, edges)
                    self.model_viewer.update()
            else:
                print("No file was selected.")
        except Exception as e:
            print(f"An error occurred while loading a file: {e}")

    def load_model(self, file: IO[str]) -> tuple[VerticesArray, EdgesIndices]:
        v_list: list[list[float]] = []
        e_list: list[list[int]] = []

        for line in file:
            parts = line.split()
            if not parts:
                continue

            if parts[0] == "v":
                v_list.append([float(x) for x in parts[1:]])
            elif parts[0] == "e":
                e_list.append([int(x) - 1 for x in parts[1:]])

        vertices = np.array(v_list, dtype=np.float32)
        edges = np.array(e_list, dtype=np.int16)

        return vertices, edges
