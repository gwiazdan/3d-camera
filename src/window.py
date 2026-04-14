from PySide6.QtWidgets import QMainWindow, QFileDialog, QWidget, QVBoxLayout
from PySide6.QtGui import QAction, QPainter, QPen, QColor
from .modeler import load_model
import numpy as np
import numpy.typing as npt


class ModelViewerWidget(QWidget):
    """A custom widget that renders 3D model using PySide6 QPainter."""

    def __init__(self):
        super().__init__()
        self.vertices: npt.NDArray[np.float32] | None = None
        self.edges: npt.NDArray[np.int16] | None = None
        self.offset: np.ndarray = np.array([0.0, 0.0])
        self.setGeometry(0, 0, 1024, 700)

    def set_model(
        self, vertices: npt.NDArray[np.float32], edges: npt.NDArray[np.int16]
    ) -> None:
        """Set the model data to be rendered."""
        self.vertices = vertices
        self.edges = edges
        self.update()

    def set_offset(self, offset: np.ndarray) -> None:
        """Set the offset for camera movement and trigger repaint."""
        self.offset = offset
        self.update()

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

        projected_vertices = [
            (int(x + self.offset[0]), int(y + self.offset[1]))
            for x, y, *_ in self.vertices
        ]

        for edge in self.edges:
            start, end = edge
            start_point = projected_vertices[start]
            end_point = projected_vertices[end]
            painter.drawLine(start_point[0], start_point[1], end_point[0], end_point[1])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Model Viewer")
        self.setGeometry(100, 100, 1024, 768)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        self.model_viewer = ModelViewerWidget()
        layout.addWidget(self.model_viewer)
        layout.setContentsMargins(0, 0, 0, 0)

        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.load_action)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        file_menu.addAction(save_action)

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
                    vertices, edges = load_model(f)
                    self.model_viewer.set_model(vertices, edges)
                    self.model_viewer.update()
            else:
                print("No file was selected.")
        except Exception as e:
            print(f"An error occurred while loading a file: {e}")
