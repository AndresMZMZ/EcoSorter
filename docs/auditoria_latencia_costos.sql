-- ============================================================================
-- CONSULTAS SQL PARA AUDITORÍA DE LATENCIA Y ANÁLISIS DE COSTOS
-- ============================================================================
-- Tabla: metricas_deteccion
-- Columnas: id, fecha_registro, objeto_detectado, latencia_yolo_ms, 
--           latencia_gemini_ms, tokens_entrada, tokens_salida, costo_estimado_usd
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. LATENCIA PROMEDIO POR TIPO DE OBJETO
-- ----------------------------------------------------------------------------
-- Objetivo: Identificar qué objetos generan mayor latencia en el sistema
SELECT 
    objeto_detectado,
    COUNT(*) AS total_detecciones,
    ROUND(AVG(latencia_yolo_ms), 2) AS avg_latencia_yolo_ms,
    ROUND(AVG(latencia_gemini_ms), 2) AS avg_latencia_gemini_ms,
    ROUND(AVG(latencia_yolo_ms + latencia_gemini_ms), 2) AS avg_latencia_total_ms
FROM metricas_deteccion
GROUP BY objeto_detectado
ORDER BY avg_latencia_total_ms DESC;

-- ----------------------------------------------------------------------------
-- 2. LATENCIA PROMEDIO GENERAL DEL SISTEMA
-- ----------------------------------------------------------------------------
-- Objetivo: Métrica general de rendimiento del sistema
SELECT 
    COUNT(*) AS total_consultas,
    ROUND(AVG(latencia_yolo_ms), 2) AS avg_latencia_yolo_ms,
    ROUND(AVG(latencia_gemini_ms), 2) AS avg_latencia_gemini_ms,
    ROUND(AVG(latencia_yolo_ms + latencia_gemini_ms), 2) AS avg_latencia_total_ms,
    ROUND(MIN(latencia_yolo_ms + latencia_gemini_ms), 2) AS min_latencia_total_ms,
    ROUND(MAX(latencia_yolo_ms + latencia_gemini_ms), 2) AS max_latencia_total_ms
FROM metricas_deteccion;

-- ----------------------------------------------------------------------------
-- 3. CONSUMO DE TOKENS POR OBJETO
-- ----------------------------------------------------------------------------
-- Objetivo: Analizar qué objetos consumen más tokens de Gemini
SELECT 
    objeto_detectado,
    COUNT(*) AS total_detecciones,
    ROUND(AVG(tokens_entrada), 2) AS avg_tokens_entrada,
    ROUND(AVG(tokens_salida), 2) AS avg_tokens_salida,
    ROUND(AVG(tokens_entrada + tokens_salida), 2) AS avg_tokens_total,
    ROUND(SUM(tokens_entrada + tokens_salida), 2) AS total_tokens_consumidos
FROM metricas_deteccion
GROUP BY objeto_detectado
ORDER BY total_tokens_consumidos DESC;

-- ----------------------------------------------------------------------------
-- 4. COSTO ESTIMADO POR OBJETO
-- ----------------------------------------------------------------------------
-- Objetivo: Identificar qué objetos son más costosos de procesar
SELECT 
    objeto_detectado,
    COUNT(*) AS total_detecciones,
    ROUND(AVG(costo_estimado_usd), 6) AS avg_costo_usd,
    ROUND(SUM(costo_estimado_usd), 6) AS total_costo_usd
FROM metricas_deteccion
GROUP BY objeto_detectado
ORDER BY total_costo_usd DESC;

-- ----------------------------------------------------------------------------
-- 5. PROYECCIÓN DE COSTO MENSUAL
-- ----------------------------------------------------------------------------
-- Objetivo: Estimar el costo mensual basado en el consumo actual
WITH daily_stats AS (
    SELECT 
        DATE(fecha_registro) AS fecha,
        COUNT(*) AS consultas_diarias,
        SUM(costo_estimado_usd) AS costo_diario_usd,
        SUM(tokens_entrada + tokens_salida) AS tokens_diarios
    FROM metricas_deteccion
    GROUP BY DATE(fecha_registro)
)
SELECT 
    ROUND(AVG(consultas_diarias), 2) AS avg_consultas_por_dia,
    ROUND(AVG(costo_diario_usd), 6) AS avg_costo_por_dia_usd,
    ROUND(AVG(tokens_diarios), 2) AS avg_tokens_por_dia,
    ROUND(AVG(costo_diario_usd) * 30, 6) AS costo_mensual_estimado_usd,
    ROUND(AVG(tokens_diarios) * 30, 2) AS tokens_mensuales_estimados
FROM daily_stats;

-- ----------------------------------------------------------------------------
-- 6. COSTO MENSUAL POR OBJETO (PROYECCIÓN)
-- ----------------------------------------------------------------------------
-- Objetivo: Distribución del costo mensual por tipo de objeto
WITH object_daily_cost AS (
    SELECT 
        objeto_detectado,
        DATE(fecha_registro) AS fecha,
        SUM(costo_estimado_usd) AS costo_objeto_dia
    FROM metricas_deteccion
    GROUP BY objeto_detectado, DATE(fecha_registro)
)
SELECT 
    objeto_detectado,
    ROUND(AVG(costo_objeto_dia), 6) AS avg_costo_por_dia_usd,
    ROUND(AVG(costo_objeto_dia) * 30, 6) AS costo_mensual_estimado_usd,
    ROUND((AVG(costo_objeto_dia) * 30) / NULLIF((SELECT AVG(costo_objeto_dia) * 30 FROM object_daily_cost), 0) * 100, 2) AS porcentaje_costo_mensual
FROM object_daily_cost
GROUP BY objeto_detectado
ORDER BY costo_mensual_estimado_usd DESC;

-- ----------------------------------------------------------------------------
-- 7. TENDENCIA DE LATENCIA EN EL TIEMPO
-- ----------------------------------------------------------------------------
-- Objetivo: Identificar si la latencia ha mejorado o empeorado
SELECT 
    DATE(fecha_registro) AS fecha,
    COUNT(*) AS total_consultas,
    ROUND(AVG(latencia_yolo_ms), 2) AS avg_latencia_yolo_ms,
    ROUND(AVG(latencia_gemini_ms), 2) AS avg_latencia_gemini_ms,
    ROUND(AVG(latencia_yolo_ms + latencia_gemini_ms), 2) AS avg_latencia_total_ms
FROM metricas_deteccion
GROUP BY DATE(fecha_registro)
ORDER BY fecha DESC;

-- ----------------------------------------------------------------------------
-- 8. TOP 10 OBJETOS MÁS FRECUENTES
-- ----------------------------------------------------------------------------
-- Objetivo: Identificar los residuos más comunes detectados
SELECT 
    objeto_detectado,
    COUNT(*) AS frecuencia,
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM metricas_deteccion), 0), 2) AS porcentaje
FROM metricas_deteccion
GROUP BY objeto_detectado
ORDER BY frecuencia DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- 9. ANÁLISIS DE OUTLIERS (LATENCIAS ANORMALES)
-- ----------------------------------------------------------------------------
-- Objetivo: Detectar consultas con latencias fuera del rango normal
SELECT 
    id,
    fecha_registro,
    objeto_detectado,
    latencia_yolo_ms,
    latencia_gemini_ms,
    (latencia_yolo_ms + latencia_gemini_ms) AS latencia_total_ms
FROM metricas_deteccion
WHERE (latencia_yolo_ms + latencia_gemini_ms) > (
    SELECT AVG(latencia_yolo_ms + latencia_gemini_ms) + 2 * STDDEV(latencia_yolo_ms + latencia_gemini_ms)
    FROM metricas_deteccion
)
ORDER BY latencia_total_ms DESC;

-- ----------------------------------------------------------------------------
-- 10. RESUMEN EJECUTIVO PARA DASHBOARD
-- ----------------------------------------------------------------------------
-- Objetivo: Vista consolidada para dashboard de monitoreo
SELECT 
    COUNT(*) AS total_consultas,
    ROUND(AVG(latencia_yolo_ms + latencia_gemini_ms), 2) AS avg_latencia_total_ms,
    ROUND(SUM(costo_estimado_usd), 6) AS costo_total_acumulado_usd,
    ROUND(SUM(tokens_entrada + tokens_salida), 2) AS tokens_totales_consumidos,
    COUNT(DISTINCT objeto_detectado) AS tipos_objetos_diferentes,
    MIN(fecha_registro) AS primera_consulta,
    MAX(fecha_registro) AS ultima_consulta
FROM metricas_deteccion;
