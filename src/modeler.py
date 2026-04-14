import numpy as np
import numpy.typing as npt
from typing import IO

VerticesArray = npt.NDArray[np.float32]
EdgesIndices = npt.NDArray[np.int16]
import pygame
from pygame.locals import *


def draw_edges(
    screen: pygame.Surface, vertices: VerticesArray, edges: EdgesIndices
) -> None:
    """
    Draw edges on the screen using pygame.

    :param screen: Pygame Surface to draw edges.
    :param vertices: Array of vertices (2D or 3D points).
    :param edges: Array of edges defined as pairs of indices into the vertices array.
    """
    projected_vertices = [(int(x), int(y)) for x, y, *_ in vertices]
    color = (255, 0, 0)
    for edge in edges:
        start, end = edge
        pygame.draw.line(
            screen, color, projected_vertices[start], projected_vertices[end]
        )


def load_model(file: IO[str]) -> tuple[VerticesArray, EdgesIndices]:
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
