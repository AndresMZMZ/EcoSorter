import base64
import os
from functools import lru_cache

import cv2
import numpy as np
from ultralytics import YOLO

from app.schemas.detection import Coordenadas, Deteccion
from app.services.waste_mapping import (
    COLORES_BBOX_BGR,
    clasificar_objeto,
    nombre_objeto_es,
    obtener_recomendacion,
)


@lru_cache(maxsize=1)
def _load_model() -> YOLO:
    model_path = os.getenv("YOLO_MODEL_PATH", "yolov8n.pt")
    return YOLO(model_path)


class DetectionService:
    def __init__(self, confidence: float = 0.35) -> None:
        self.confidence = float(os.getenv("YOLO_CONFIDENCE", str(confidence)))

    def detect(self, frame: np.ndarray) -> list[Deteccion]:
        model = _load_model()
        results = model(frame, conf=self.confidence, verbose=False)
        detecciones: list[Deteccion] = []

        for result in results:
            if result.boxes is None:
                continue

            for idx, box in enumerate(result.boxes, start=1):
                class_id = int(box.cls[0])
                class_name = model.names[class_id]

                if class_name == "person":
                    continue

                categoria = clasificar_objeto(class_name)
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                detecciones.append(
                    Deteccion(
                        id=idx,
                        nombre=nombre_objeto_es(class_name),
                        categoria=categoria.categoria,
                        color_caja=categoria.color_caja,
                        coordenadas=Coordenadas(x1=x1, y1=y1, x2=x2, y2=y2),
                        confianza=round(float(box.conf[0]), 4),
                        recomendacion=obtener_recomendacion(class_name, categoria.color_caja),
                    )
                )

        return detecciones

    def draw_detections(
        self, frame: np.ndarray, detecciones: list[Deteccion]
    ) -> np.ndarray:
        annotated = frame.copy()

        for det in detecciones:
            color = COLORES_BBOX_BGR.get(det.color_caja, (0, 0, 220))
            x1, y1, x2, y2 = (
                det.coordenadas.x1,
                det.coordenadas.y1,
                det.coordenadas.x2,
                det.coordenadas.y2,
            )

            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            if det.color_caja == "blanca":
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 0), 1)

            label = f"{det.nombre} [{det.color_caja}]"
            (text_w, text_h), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            cv2.rectangle(
                annotated,
                (x1, max(y1 - text_h - 8, 0)),
                (x1 + text_w + 4, y1),
                color,
                -1,
            )
            text_color = (0, 0, 0) if det.color_caja in {"blanca", "amarilla"} else (255, 255, 255)
            cv2.putText(
                annotated,
                label,
                (x1 + 2, max(y1 - 4, text_h)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                text_color,
                1,
                cv2.LINE_AA,
            )

        return annotated

    def frame_to_base64(self, frame: np.ndarray) -> str:
        success, buffer = cv2.imencode(".jpg", frame)
        if not success:
            raise RuntimeError("No se pudo codificar el frame a JPEG")
        return base64.b64encode(buffer).decode("utf-8")

    def decode_base64_image(self, image_base64: str) -> np.ndarray:
        payload = image_base64.strip()
        if "," in payload:
            payload = payload.split(",", 1)[1]

        image_bytes = base64.b64decode(payload)
        array = np.frombuffer(image_bytes, dtype=np.uint8)
        frame = cv2.imdecode(array, cv2.IMREAD_COLOR)

        if frame is None:
            raise ValueError("La imagen enviada no es válida o no se pudo decodificar")

        return frame


detection_service = DetectionService()
