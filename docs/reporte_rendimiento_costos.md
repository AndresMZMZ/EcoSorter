# Reporte de Rendimiento y Costos - EcoSorter

**Fecha:** 17 de julio de 2026  
**Responsable:** Daniel (Scrum Master y QA)  
**Colaborador:** Camilo (Arquitecto Cloud y DevOps)

---

## Resumen Ejecutivo

Este reporte presenta el análisis de rendimiento y costos del sistema EcoSorter, basado en las métricas registradas en Supabase. El objetivo es optimizar el rendimiento de la aplicación y controlar los costos asociados al uso de la API de Gemini.

---

## Métricas Monitoreadas

### 1. Latencia del Sistema
- **Latencia YOLO:** Tiempo de detección de objetos con YOLOv8 (en ms)
- **Latencia Gemini:** Tiempo de clasificación con Gemini Vision (en ms)
- **Latencia Total:** Suma de ambas latencias

### 2. Consumo de Tokens
- **Tokens de Entrada:** Tokens enviados a Gemini (imagen + prompt)
- **Tokens de Salida:** Tokens generados por Gemini (respuesta JSON)

### 3. Costos
- **Costo Estimado:** Calculado basándose en precios de Gemini Flash
  - Input: $0.075 por 1M tokens
  - Output: $0.30 por 1M tokens

---

## Consultas de Análisis

Las consultas SQL para análisis están disponibles en `docs/auditoria_latencia_costos.sql`:

### Consultas Principales

1. **Latencia Promedio por Objeto** - Identifica objetos con mayor latencia
2. **Latencia Promedio General** - Métrica global del sistema
3. **Consumo de Tokens por Objeto** - Análisis de consumo por tipo de residuo
4. **Costo Estimado por Objeto** - Identifica objetos más costosos
5. **Proyección de Costo Mensual** - Estima gasto mensual basado en uso actual
6. **Tendencia de Latencia** - Evolución del rendimiento en el tiempo
7. **Top 10 Objetos Más Frecuentes** - Residuos más comunes
8. **Análisis de Outliers** - Detecta latencias anormales
9. **Resumen Ejecutivo** - Vista consolidada para dashboard

---

## Uso de las Consultas

### Ejecución en Supabase

1. Acceder al dashboard de Supabase: https://supabase.com/dashboard
2. Ir a la sección SQL Editor
3. Copiar las consultas desde `docs/auditoria_latencia_costos.sql`
4. Ejecutar cada consulta según el análisis requerido

### Ejemplo: Proyección de Costo Mensual

```sql
-- Consulta 5: Proyección de Costo Mensual
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
```

---

## KPIs Recomendados

### Rendimiento
- **Latencia Total Promedio:** < 2000ms (objetivo)
- **Latencia YOLO Promedio:** < 100ms
- **Latencia Gemini Promedio:** < 1900ms

### Costos
- **Costo por Consulta:** < $0.0001
- **Costo Mensual Estimado:** < $10 (para 100k consultas/mes)

### Frecuencia
- **Top 5 Objetos:** Deben representar > 60% de las consultas
- **Outliers:** < 5% de consultas con latencia > 2 desviaciones estándar

---

## Acciones de Optimización

### Si la latencia es alta:
1. Revisar modelo YOLO: considerar modelo más ligero (YOLOv8n vs YOLOv8s)
2. Optimizar tamaño de imagen enviada a Gemini
3. Implementar caché para objetos frecuentes

### Si el costo es alto:
1. Revisar prompt de Gemini para reducir tokens de entrada
2. Considerar modelo más económico (Gemini Flash vs Pro)
3. Implementar límites de uso por usuario

---

## Próximos Pasos

1. **Automatización:** Crear dashboard en Supabase Studio con visualizaciones
2. **Alertas:** Configurar notificaciones cuando latencia/costo supen umbrales
3. **Reporte Semanal:** Generar reporte automático cada semana
4. **Optimización:** Iterar basándose en datos recolectados

---

## Archivos Relacionados

- `backend/app/services/supabase_service.py` - Servicio de registro de métricas
- `backend/app/services/gemini_service.py` - Captura de metadatos de Gemini
- `backend/app/routers/detection.py` - Integración de métricas en endpoints
- `docs/auditoria_latencia_costos.sql` - Consultas SQL para análisis

---

## Contacto

Para preguntas sobre este reporte:
- **Daniel:** Scrum Master y QA
- **Camilo:** Arquitecto Cloud y DevOps
