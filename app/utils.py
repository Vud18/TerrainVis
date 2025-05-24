import os
from pathlib import Path
from typing import Optional, List, Tuple

import yaml
import pandas as pd
import geojson
from shapely.geometry import Polygon


def load_config(path=None):
    if path is None:
        base_dir = os.getcwd()  # рабочая директория, где запускается процесс
        path = os.path.join(base_dir, 'config.yaml')
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_elevation_matrix(config: dict) -> pd.DataFrame:
    """
    Загружает матрицу высот из CSV-файла на основе конфигурации.
    """
    csv_path = config.get('matrix_path')
    df = pd.read_csv(csv_path, header=None)

    expected_shape = (
        config.get('matrix_height'),
        config.get('matrix_width')
    )

    if df.shape != expected_shape:
        raise ValueError(f"Expected shape {expected_shape}, got {df.shape}")

    return df.to_numpy()


def is_within_bounds(x: int, y: int, width: int, height: int) -> bool:
    """
    Проверяет, находится ли точка (x, y) в пределах указанных границ.
    """
    return 0 <= x < width and 0 <= y < height


def export_geojson(points: List[Tuple[int, int]], filename: str | Path) -> Optional[str]:
    """
    Сохраняет список точек как geoJSON-многоугольник в файл.

    :param points: Список точек [(x, y)]
    :param filename: Путь к файлу GeoJSON
    :return: Имя файла или None, если точек недостаточно
    """
    if len(points) < 3:
        return None

    polygon = Polygon(points).convex_hull
    geojson_obj = geojson.Feature(
        geometry=geojson.Polygon([list(polygon.exterior.coords)]),
        properties={}
    )

    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    with filename.open('w', encoding='utf-8') as f:
        geojson.dump(geojson_obj, f)

    return str(filename)
