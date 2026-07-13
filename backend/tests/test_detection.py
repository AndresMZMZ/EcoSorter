import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.detection import Coordenadas, Deteccion
from app.services.waste_mapping import clasificar_objeto

client = TestClient(app)


def test_clasificar_objeto_categorias():
    assert clasificar_objeto("bottle").color_caja == "blanca"
    assert clasificar_objeto("apple").color_caja == "verde"
    assert clasificar_objeto("toilet").color_caja == "negra"
    assert clasificar_objeto("battery").color_caja == "amarilla"
    assert clasificar_objeto("chair").color_caja == "roja"


def test_detect_camera_frame_sin_camara(monkeypatch):
    def _fail_read():
        raise RuntimeError("Cámara no disponible")

    monkeypatch.setattr(
        "app.routers.detection.camera_service.read_frame", _fail_read
    )
    response = client.get("/detect/camera/frame")
    assert response.status_code == 503


def test_detect_image_sin_payload():
    response = client.post("/detect/image", json={"image_base64": None})
    assert response.status_code == 400


def test_detect_image_con_mock(monkeypatch):
    fake_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    fake_detecciones = [
        Deteccion(
            id=1,
            nombre="Botella",
            categoria="Residuos aprovechables",
            color_caja="blanca",
            coordenadas=Coordenadas(x1=10, y1=20, x2=50, y2=80),
            confianza=0.91,
        )
    ]

    monkeypatch.setattr(
        "app.routers.detection.detection_service.decode_base64_image",
        lambda _: fake_frame,
    )
    monkeypatch.setattr(
        "app.routers.detection.detection_service.detect",
        lambda _: fake_detecciones,
    )
    monkeypatch.setattr(
        "app.routers.detection.detection_service.draw_detections",
        lambda frame, dets: frame,
    )
    monkeypatch.setattr(
        "app.routers.detection.detection_service.frame_to_base64",
        lambda _: "ZmFrZQ==",
    )

    response = client.post(
        "/detect/image",
        json={"image_base64": "aGVsbG8="},
        params={"include_frame": True},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["detecciones"]) == 1
    det = data["detecciones"][0]
    assert det["id"] == 1
    assert det["nombre"] == "Botella"
    assert det["color_caja"] == "blanca"
    assert det["coordenadas"]["x1"] == 10
    assert data["frame_base64"] == "ZmFrZQ=="
