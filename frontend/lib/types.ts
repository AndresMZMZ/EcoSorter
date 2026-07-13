export type ColorCaja = "blanca" | "verde" | "negra" | "amarilla" | "roja";

export interface Coordenadas {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface Deteccion {
  id: number;
  nombre: string;
  categoria: string;
  color_caja: ColorCaja;
  coordenadas: Coordenadas;
  confianza: number;
  recomendacion: string;
}

export interface DeteccionResponse {
  detecciones: Deteccion[];
  frame_base64: string | null;
  error: string | null;
}
