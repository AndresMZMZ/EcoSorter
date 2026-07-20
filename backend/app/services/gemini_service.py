import base64
import json
import os
import time
from dataclasses import dataclass
from dotenv import load_dotenv

import google.generativeai as genai

from app.schemas.detection import Coordenadas, Deteccion, DeteccionResponse


@dataclass
class GeminiMetadata:
    """Metadatos de una llamada a la API de Gemini."""
    latencia_ms: float
    tokens_entrada: int
    tokens_salida: int
    costo_estimado_usd: float


_SYSTEM_PROMPT = """\
Eres un experto en clasificación de residuos sólidos urbanos. Tu única función es \
analizar imágenes de objetos y clasificar cada residuo visible según las siguientes \
categorías de contenedor:

- blanca: residuos aprovechables (papel, cartón, plástico, vidrio, metales limpios).
- verde: residuos orgánicos (restos de comida, cáscaras, desechos vegetales).
- negra: residuos no reciclables o contaminados (servilletas usadas, papel higiénico, \
residuos sucios).
- amarilla: baterías y pilas (pilas AA/AAA, baterías de celular, pilas de controles).
- roja: otros residuos que no encajan en las categorías anteriores.

REGLAS ESTRICTAS:
1. SOLO clasificas residuos. Si la imagen no contiene residuos, retorna un JSON con \
un arreglo vacío: {"items": []}.
2. NO inventes objetos que no existan en la imagen.
3. Para cada residuo detectado, indica un nombre descriptivo en español, la categoría \
de color del contenedor, y una recomendación práctica de disposición.
4. Responde EXCLUSIVAMENTE con el siguiente formato JSON válido, sin texto adicional:

{
  "items": [
    {
      "nombre": "Nombre del objeto en español",
      "color_caja": "blanca|verde|negra|amarilla|roja",
      "recomendacion": "Recomendación breve y práctica"
    }
  ]
}

Si hay múltiples residuos, inclúyelos todos en el arreglo.\
"""


class GeminiClassificationService:
    _instance: "GeminiClassificationService | None" = None

    def __new__(cls) -> "GeminiClassificationService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY", "")
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

        if not api_key:
            self._model = None
            self._initialized = True
            return

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=_SYSTEM_PROMPT,
        )
        self._initialized = True

    def classify(self, image_base64: str) -> tuple[DeteccionResponse, GeminiMetadata | None]:
        empty = DeteccionResponse(detecciones=[], frame_base64=None)
        empty_metadata = GeminiMetadata(latencia_ms=0, tokens_entrada=0, tokens_salida=0, costo_estimado_usd=0)

        if self._model is None:
            return DeteccionResponse(
                detecciones=[], frame_base64=None,
                error="GEMINI_API_KEY no está configurada. Agrécala al archivo .env.",
            ), None

        try:
            payload = image_base64.strip()
            if "," in payload:
                payload = payload.split(",", 1)[1]

            image_part = {"inline_data": {"mime_type": "image/jpeg", "data": payload}}

            start_time = time.time()
            response = self._model.generate_content(
                [image_part, "Clasifica los residuos visibles en esta imagen."]
            )
            end_time = time.time()
            latencia_ms = (end_time - start_time) * 1000

            text = response.text.strip()

            if text.startswith("```"):
                lines = text.split("\n")
                lines = [l for l in lines if not l.strip().startswith("```")]
                text = "\n".join(lines)

            data = json.loads(text)
            items = data.get("items", [])

            # Capturar tokens de la respuesta
            tokens_entrada = response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0
            tokens_salida = response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0
            
            # Calcular costo estimado (precios aproximados de Gemini Flash)
            # Input: $0.075 por 1M tokens, Output: $0.30 por 1M tokens
            costo_estimado_usd = (tokens_entrada * 0.075 / 1_000_000) + (tokens_salida * 0.30 / 1_000_000)

            metadata = GeminiMetadata(
                latencia_ms=latencia_ms,
                tokens_entrada=tokens_entrada,
                tokens_salida=tokens_salida,
                costo_estimado_usd=costo_estimado_usd,
            )
        except Exception as exc:
            return DeteccionResponse(
                detecciones=[], frame_base64=None,
                error=f"Error al consultar Gemini: {exc}",
            ), None

        detecciones: list[Deteccion] = []
        cero = Coordenadas(x1=0, y1=0, x2=0, y2=0)

        for idx, item in enumerate(items, start=1):
            color = item.get("color_caja", "roja")
            detecciones.append(
                Deteccion(
                    id=idx,
                    nombre=item.get("nombre", "Desconocido"),
                    categoria=_categoria_label(color),
                    color_caja=color,
                    coordenadas=cero,
                    confianza=0.0,
                    recomendacion=item.get("recomendacion", ""),
                )
            )

        return DeteccionResponse(detecciones=detecciones, frame_base64=None), metadata


def _categoria_label(color_caja: str) -> str:
    labels = {
        "blanca": "Residuos aprovechables",
        "verde": "Residuos orgánicos",
        "negra": "Residuos no reciclables o contaminados",
        "amarilla": "Baterías y pilas",
        "roja": "Otros residuos no reciclables",
    }
    return labels.get(color_caja, "Otros residuos no reciclables")


gemini_service = GeminiClassificationService()
