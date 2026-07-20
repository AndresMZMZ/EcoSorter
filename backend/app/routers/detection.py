import json
import time

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse

from app.schemas.detection import DeteccionResponse, ImageDetectRequest
from app.services.camera_service import camera_service
from app.services.detection_service import detection_service
from app.services.gemini_service import gemini_service
from app.services.supabase_service import supabase_service

router = APIRouter(prefix="/detect", tags=["Detección"])


def _build_response(frame, include_frame: bool) -> DeteccionResponse:
    detecciones = detection_service.detect(frame)
    frame_base64 = None

    if include_frame:
        annotated = detection_service.draw_detections(frame, detecciones)
        frame_base64 = detection_service.frame_to_base64(annotated)

    return DeteccionResponse(detecciones=detecciones, frame_base64=frame_base64)


@router.get("/camera/frame", response_model=DeteccionResponse)
def detect_camera_frame(
    include_frame: bool = Query(
        default=True,
        description="Incluir el frame anotado codificado en base64",
    ),
):
    """Captura un frame de la cámara, detecta objetos con YOLOv8 y los clasifica."""
    try:
        frame = camera_service.read_frame()
        return _build_response(frame, include_frame)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/camera/video")
def detect_camera_video(
    fps: int = Query(default=10, ge=1, le=30, description="Frames por segundo del stream"),
):
    """Stream MJPEG de la cámara con detecciones YOLOv8 dibujadas en tiempo real."""

    def generate_stream():
        delay = 1.0 / fps
        while True:
            try:
                frame = camera_service.read_frame()
                detecciones = detection_service.detect(frame)
                annotated = detection_service.draw_detections(frame, detecciones)
                success, buffer = cv2.imencode(
                    ".jpg", annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 80]
                )
                if not success:
                    continue

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
                )
                time.sleep(delay)
            except RuntimeError:
                break

    try:
        camera_service.read_frame()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return StreamingResponse(
        generate_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.post("/image", response_model=DeteccionResponse)
async def detect_image_from_base64(
    request: ImageDetectRequest,
    include_frame: bool = Query(default=True),
):
    """Detecta y clasifica objetos en una imagen enviada en base64."""
    if not request.image_base64:
        raise HTTPException(
            status_code=400,
            detail="Debe enviar image_base64 en el cuerpo de la petición",
        )

    try:
        frame = detection_service.decode_base64_image(request.image_base64)
        return _build_response(frame, include_frame)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/image/upload", response_model=DeteccionResponse)
async def detect_image_upload(
    file: UploadFile = File(...),
    include_frame: bool = Query(default=True),
):
    """Detecta y clasifica objetos en una imagen enviada como archivo."""
    try:
        contents = await file.read()
        array = np.frombuffer(contents, dtype=np.uint8)
        frame = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("El archivo enviado no es una imagen válida")
        return _build_response(frame, include_frame)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/gemini", response_model=DeteccionResponse)
async def detect_with_gemini(request: ImageDetectRequest):
    """Clasifica residuos en una imagen usando Gemini 2.5 Vision."""
    if not request.image_base64:
        raise HTTPException(
            status_code=400,
            detail="Debe enviar image_base64 en el cuerpo de la petición",
        )

    try:
        start_time = time.time()
        response, metadata = gemini_service.classify(request.image_base64)
        
        if metadata and response.detecciones:
            # Obtener el objeto detectado principal
            objeto_detectado = response.detecciones[0].nombre if response.detecciones else "Desconocido"
            
            # Registrar métricas en Supabase
            supabase_service.registrar_metrica(
                objeto_detectado=objeto_detectado,
                latencia_yolo_ms=0,  # Este endpoint no usa YOLO
                latencia_gemini_ms=metadata.latencia_ms,
                tokens_entrada=metadata.tokens_entrada,
                tokens_salida=metadata.tokens_salida,
                costo_estimado_usd=metadata.costo_estimado_usd,
            )
        
        return response
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Gemini no respondió un JSON válido: {exc}",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Error al comunicarse con Gemini: {exc}",
        ) from exc
