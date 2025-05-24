from fastapi import Form

from typing import Annotated
from pydantic import BaseModel, Field


class AnalyzeForm(BaseModel):
    """
    Модель данных формы анализа зоны видимости станции.

    Атрибуты:
        x_coordinate (int): Координата X станции (в пределах размера матрицы).
        y_coordinate (int): Координата Y станции.
        station_height (float): Высота станции в метрах, должна быть положительной.
        view_radius (int): Радиус обзора в ячейках, должен быть положительным.
    """

    x_coordinate: Annotated[
        int,
        Field(ge=0, le=1000, description="Координата X станции", examples=[100])
    ]
    y_coordinate: Annotated[
        int,
        Field(ge=0, le=1000, description="Координата Y станции", examples=[200])
    ]
    station_height: Annotated[
        float,
        Field(gt=0, description="Высота станции в метрах", examples=[10.5])
    ]
    view_radius: Annotated[
        int,
        Field(gt=0, description="Радиус обзора в ячейках", examples=[5])
    ]

    @classmethod
    def as_form(
            cls,
            x: int = Form(..., alias="x"),
            y: int = Form(..., alias="y"),
            height: float = Form(..., alias="height"),
            r: int = Form(..., alias="r")
    ):
        """
        Метод для преобразования HTML-формы в экземпляр Pydantic-модели,
        совместимый с FastAPI Form() binding.

        Параметры:
            x (int): Координата X.
            y (int): Координата Y.
            height (float): Высота станции.
            r (int): Радиус обзора.

        Возвращает:
            AnalyzeForm: экземпляр модели с данными формы.
        """
        return cls(
            x_coordinate=x,
            y_coordinate=y,
            station_height=height,
            view_radius=r
        )
