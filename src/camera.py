from PySide6.QtCore import Qt
import numpy as np

from src.window import VerticesArray

from src.config import settings


class Camera:
    def __init__(self, vertices: VerticesArray):
        self._vertices: VerticesArray = vertices
        self.position = np.array([0.0, 0.0, -500.0], dtype=np.float32)
        self.angles = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.pressed_keys = set()
        self.focal_length = settings.camera.default_fov

    def update_state(self, width: int, height: int) -> VerticesArray:
        if not self.pressed_keys:
            return self._get_transformed_vertices(width, height)

        dr = float(settings.camera.translation_speed)
        dangle = np.radians(settings.camera.rotation_speed)

        if Qt.Key.Key_W in self.pressed_keys:
            self.position[2] += dr
        if Qt.Key.Key_S in self.pressed_keys:
            self.position[2] -= dr
        if Qt.Key.Key_A in self.pressed_keys:
            self.position[0] -= dr
        if Qt.Key.Key_D in self.pressed_keys:
            self.position[0] += dr
        if Qt.Key.Key_Space in self.pressed_keys:
            self.position[1] += dr
        if Qt.Key.Key_Shift in self.pressed_keys:
            self.position[1] -= dr

        if Qt.Key.Key_Q in self.pressed_keys:
            self.angles[0] -= dangle
        if Qt.Key.Key_E in self.pressed_keys:
            self.angles[0] += dangle
        if Qt.Key.Key_R in self.pressed_keys:
            self.angles[1] -= dangle
        if Qt.Key.Key_T in self.pressed_keys:
            self.angles[1] += dangle
        if Qt.Key.Key_F in self.pressed_keys:
            self.angles[2] -= dangle
        if Qt.Key.Key_G in self.pressed_keys:
            self.angles[2] += dangle

        if Qt.Key.Key_Equal in self.pressed_keys:
            self.focal_length += settings.camera.fov_change_speed
        if Qt.Key.Key_Minus in self.pressed_keys:
            self.focal_length -= 10.0

        return self._get_transformed_vertices(width, height)

    def _get_transformed_vertices(self, width: int, height: int) -> VerticesArray:
        ones = np.ones((self._vertices.shape[0], 1), dtype=np.float32)
        v = np.hstack([self._vertices, ones])
        T = np.eye(4, dtype=np.float32)
        T[:3, 3] = -self.position

        ax, ay, az = np.radians(self.angles)

        Rx = np.array(
            [
                [1, 0, 0, 0],
                [0, np.cos(ax), -np.sin(ax), 0],
                [0, np.sin(ax), np.cos(ax), 0],
                [0, 0, 0, 1],
            ],
            dtype=np.float32,
        )
        Ry = np.array(
            [
                [np.cos(ay), 0, np.sin(ay), 0],
                [0, 1, 0, 0],
                [-np.sin(ay), 0, np.cos(ay), 0],
                [0, 0, 0, 1],
            ],
            dtype=np.float32,
        )
        Rz = np.array(
            [
                [np.cos(az), -np.sin(az), 0, 0],
                [np.sin(az), np.cos(az), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ],
            dtype=np.float32,
        )

        R_view = Rx @ Ry @ Rz
        MV = R_view @ T

        f = self.focal_length
        aspect_ratio = width / max(height, 1)

        P = np.array(
            [[f / aspect_ratio, 0, 0, 0], [0, f, 0, 0], [0, 0, 1, 0], [0, 0, 1, 0]],
            dtype=np.float32,
        )

        v_final = v @ (P @ MV).T
        w = v_final[:, 3:4]
        mask = w[:, 0] > 0.1

        res = np.zeros((v.shape[0], 3), dtype=np.float32)

        res[mask, 0] = v_final[mask, 0] / w[mask, 0] + (width / 2)
        res[mask, 1] = (height / 2) - (v_final[mask, 1] / w[mask, 0])
        res[mask, 2] = w[mask, 0]
        return res
