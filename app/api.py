from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .schemas import AnalyzeForm
from .utils import load_config, load_elevation_matrix, export_geojson
from .logic import compute_visibility_polygon, plot_visibility
from .core.paths import STATIC_DIR

import uuid

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def form_view(request: Request) -> HTMLResponse:
    """
    Отображает главную страницу с HTML-формой для ввода координат станции и параметров анализа.

    Args:
        request (Request): Объект запроса FastAPI.

    Returns:
        HTMLResponse: Отрендеренный шаблон формы.
    """
    return templates.TemplateResponse("form.html", {"request": request})


@router.post("/analyze", response_class=HTMLResponse)
async def analyze(
        request: Request,
        form_data: AnalyzeForm = Depends(AnalyzeForm.as_form),
):
    """
        Обрабатывает форму анализа зоны видимости.

        1. Загружает данные конфигурации и матрицу высот.
        2. Вычисляет зону видимости.
        3. Сохраняет результаты в виде GeoJSON и PNG.
        4. Возвращает HTML-шаблон со ссылками на результаты.

        Args:
            request (Request): Объект запроса.
            form_data (AnalyzeForm): Данные формы, автоматически маппятся через Depends.

        Returns:
            HTMLResponse: Отрендеренный шаблон с результатами анализа.
        """

    config = load_config()
    matrix = load_elevation_matrix(config)

    points = compute_visibility_polygon(
        form_data.x_coordinate,
        form_data.y_coordinate,
        form_data.view_radius,
        matrix,
        form_data.station_height
    )

    unique_id = uuid.uuid4().hex
    geojson_path = STATIC_DIR / f"visibility_zone_{unique_id}.geojson"
    png_path = STATIC_DIR / f"visibility_{unique_id}.png"

    export_geojson(points, str(geojson_path))
    plot_visibility(
        matrix,
        points,
        form_data.x_coordinate,
        form_data.y_coordinate,
        output_file=str(png_path)
    )

    return templates.TemplateResponse("form.html", {
        "request": request,
        "message": "Результат готов!",
        "geojson_url": f"/static/{geojson_path.name}",
        "png_url": f"/static/{png_path.name}"
    })
