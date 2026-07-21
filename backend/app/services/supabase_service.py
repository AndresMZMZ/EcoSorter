import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client


class SupabaseMetricsService:
    _instance: "SupabaseMetricsService | None" = None

    def __new__(cls) -> "SupabaseMetricsService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        load_dotenv()
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            self._client = None
            self._initialized = True
            return
        
        self._client: Client = create_client(supabase_url, supabase_key)
        self._table_name = "metricas_deteccion"
        self._initialized = True

    def is_available(self) -> bool:
        """Verifica si el cliente de Supabase está configurado."""
        return self._client is not None

    def registrar_metrica(
        self,
        objeto_detectado: str,
        latencia_yolo_ms: float,
        latencia_gemini_ms: float,
        tokens_entrada: int,
        tokens_salida: int,
        costo_estimado_usd: float,
    ) -> bool:
        """
        Registra una métrica de detección en Supabase.
        
        Args:
            objeto_detectado: Nombre del objeto detectado
            latencia_yolo_ms: Latencia de detección YOLO en milisegundos
            latencia_gemini_ms: Latencia de clasificación Gemini en milisegundos
            tokens_entrada: Tokens de entrada consumidos por Gemini
            tokens_salida: Tokens de salida consumidos por Gemini
            costo_estimado_usd: Costo estimado en USD
            
        Returns:
            True si se registró exitosamente, False en caso contrario
        """
        if not self.is_available():
            print("Supabase no está configurado. No se registrará la métrica.")
            return False
        
        try:
            data = {
                "fecha_registro": datetime.utcnow().isoformat(),
                "objeto_detectado": objeto_detectado,
                "latencia_yolo_ms": latencia_yolo_ms,
                "latencia_gemini_ms": latencia_gemini_ms,
                "tokens_entrada": tokens_entrada,
                "tokens_salida": tokens_salida,
                "costo_estimado_usd": costo_estimado_usd,
            }
            
            response = self._client.table(self._table_name).insert(data).execute()
            
            if response.data:
                print(f"Métrica registrada exitosamente: {objeto_detectado}")
                return True
            else:
                print(f"Error al registrar métrica: {response}")
                return False
                
        except Exception as exc:
            print(f"Excepción al registrar métrica en Supabase: {exc}")
            return False


supabase_service = SupabaseMetricsService()
