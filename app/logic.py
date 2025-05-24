import math
from typing import List, Tuple

import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

from .utils import is_within_bounds

Point = Tuple[int, int]


def bresenham_line(x0: int, y0: int, x1: int, y1: int) -> List[Point]:
    """
    Алгоритм Брезенхэма для получения всех точек линии между двумя координатами.
    """
    points = []
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    x, y = x0, y0
    sx = 1 if x1 > x0 else -1
    sy = 1 if y1 > y0 else -1

    if dx > dy:
        err = dx / 2.0
        while x != x1:
            points.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            points.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy

    points.append((x1, y1))
    return points


def is_visible(
        x0: int, y0: int, h_station: float,
        x1: int, y1: int,
        matrix: np.ndarray
) -> bool:
    """
    Проверка, видна ли точка (x1, y1) с точки (x0, y0), учитывая высоты.
    """
    line = bresenham_line(x0, y0, x1, y1)
    z0 = matrix[y0][x0] + h_station
    z1 = matrix[y1][x1]
    total_dist = math.hypot(x1 - x0, y1 - y0)

    for idx, (x, y) in enumerate(line[1:-1], start=1):
        dist = math.hypot(x - x0, y - y0)
        expected_z = z0 + (z1 - z0) * (dist / total_dist)
        terrain_z = matrix[y][x]
        if terrain_z > expected_z:
            return False
    return True


def compute_visibility_polygon(
        x0: int,
        y0: int,
        radius: int,
        matrix: np.ndarray,
        h_station: float
) -> List[Point]:
    """
    Вычисляет все видимые точки из заданной станции в пределах радиуса.
    """
    visible_points = []

    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            x, y = x0 + dx, y0 + dy
            if not is_within_bounds(x, y, matrix.shape[1], matrix.shape[0]):
                continue

            if math.hypot(dx, dy) <= radius and is_visible(x0, y0, h_station, x, y, matrix):
                visible_points.append((x, y))

    return visible_points


def plot_visibility(
        matrix: np.ndarray,
        visible_points: List[Point],
        station_x: int,
        station_y: int,
        output_file: str = "static/visibility.png"
) -> None:
    """
    Визуализирует матрицу высот и зону видимости.

    :param matrix: Матрица высот (numpy array)
    :param visible_points: Список видимых точек [(x1,y1), ...]
    :param station_x: X-координата станции
    :param station_y: Y-координата станции
    :param output_file: Имя файла для сохранения
    """
    plt.figure(figsize=(10, 8))
    plt.imshow(matrix, cmap='terrain', alpha=0.7)
    plt.colorbar(label='Высота (м)')

    # Станция
    plt.scatter([station_x], [station_y], c='red', s=100, label='Станция')

    # Видимые точки
    if visible_points:
        xs, ys = zip(*visible_points)
        plt.scatter(xs, ys, c='blue', s=5, alpha=0.5, label='Видимая зона')

    # Контур полигона
    if len(visible_points) >= 3:
        polygon = Polygon(visible_points).convex_hull
        x, y = polygon.exterior.xy
        plt.plot(x, y, color='green', linewidth=2, label='Граница видимости')

    plt.title("Зона видимости станции")
    plt.xlabel("X координата")
    plt.ylabel("Y координата")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(output_file, dpi=300)
    plt.close()
