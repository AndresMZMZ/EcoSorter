from pydantic import BaseModel, Field


class Coordenadas(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int


class Deteccion(BaseModel):
    id: int
    nombre: str
    categoria: str
    color_caja: str
    coordenadas: Coordenadas
    confianza: float = Field(ge=0.0, le=1.0)
    recomendacion: str = ""


class DeteccionResponse(BaseModel):
    detecciones: list[Deteccion]
    frame_base64: str | None = None
    error: str | None = None


class ImageDetectRequest(BaseModel):
    image_base64: str | None = None
