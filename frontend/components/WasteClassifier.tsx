"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { detectImageBase64, detectImageGemini } from "@/lib/api";
import type { ColorCaja, Deteccion } from "@/lib/types";

const SCAN_INTERVAL_MS = 1800;
const GEMINI_MIN_CONFIDENCE = 0.70;
const HIGH_CONFIDENCE = 0.90;
const COOLDOWN_SECONDS = 15;
const COOLDOWN_SECONDS_HIGH = 10;

const GUIA_CLASIFICACION: Array<{
  color: ColorCaja;
  etiqueta: string;
  descripcion: string;
  ejemplos: string;
}> = [
  {
    color: "blanca",
    etiqueta: "Caja blanca",
    descripcion: "Residuos aprovechables",
    ejemplos: "Papel, cartón, plástico, vidrio y metales limpios",
  },
  {
    color: "verde",
    etiqueta: "Caja verde",
    descripcion: "Residuos orgánicos",
    ejemplos: "Restos de comida, cáscaras, desechos vegetales",
  },
  {
    color: "negra",
    etiqueta: "Caja negra",
    descripcion: "No reciclables o contaminados",
    ejemplos: "Servilletas usadas, papel higiénico, residuos sucios",
  },
  {
    color: "amarilla",
    etiqueta: "Caja amarilla",
    descripcion: "Baterías y pilas",
    ejemplos: "Pilas AA/AAA, baterías de celular o control remoto",
  },
  {
    color: "roja",
    etiqueta: "Caja roja",
    descripcion: "Otros residuos",
    ejemplos: "Objetos que no son reciclables en contenedores comunes",
  },
];

const COLOR_LABEL: Record<ColorCaja, string> = {
  blanca: "Blanco",
  verde: "Verde",
  negra: "Negro",
  amarilla: "Amarillo",
  roja: "Rojo",
};

function captureFrame(video: HTMLVideoElement, canvas: HTMLCanvasElement): string {
  const context = canvas.getContext("2d");
  if (!context || video.videoWidth === 0) {
    throw new Error("La cámara aún no está lista para capturar.");
  }

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  const dataUrl = canvas.toDataURL("image/jpeg", 0.85);
  return dataUrl.split(",")[1];
}

function startCooldown(
  ref: React.MutableRefObject<number>,
  setter: (v: number) => void,
  seconds: number,
  setDuration: (v: number) => void,
) {
  ref.current = Date.now() + seconds * 1000;
  setter(seconds * 1000);
  setDuration(seconds);
}

function pickBest(detections: Deteccion[]): Deteccion[] {
  if (detections.length <= 1) return detections;
  return [...detections].sort((a, b) => b.confianza - a.confianza);
}

function speakText(text: string, lang: string = "es-CO"): void {
  if (!("speechSynthesis" in window)) {
    console.warn("Web Speech API no está disponible en este navegador.");
    return;
  }

  // Cancelar cualquier speech anterior
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang;
  utterance.rate = 1.0;
  utterance.pitch = 1.0;
  utterance.volume = 1.0;

  window.speechSynthesis.speak(utterance);
}

export default function WasteClassifier() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const scanningRef = useRef(false);
  const lastDetectionNameRef = useRef<string | null>(null);

  const [cameraActive, setCameraActive] = useState(false);
  const [autoScan, setAutoScan] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [detecciones, setDetecciones] = useState<Deteccion[]>([]);
  const [annotatedFrame, setAnnotatedFrame] = useState<string | null>(null);
  const [lastScanAt, setLastScanAt] = useState<string | null>(null);

  const [geminiFrame, setGeminiFrame] = useState<string | null>(null);
  const [isGeminiLoading, setIsGeminiLoading] = useState(false);
  const cooldownEndRef = useRef(0);
  const [cooldownRemaining, setCooldownRemaining] = useState(0);
  const [lowConfidenceScan, setLowConfidenceScan] = useState(false);

  const [cooldownDuration, setCooldownDuration] = useState(COOLDOWN_SECONDS);
  const [cooldownPaused, setCooldownPaused] = useState(false);
  const cooldownPausedRef = useRef(false);
  const pausedRemainingRef = useRef(0);

  const isBlocked = isGeminiLoading || cooldownRemaining > 0;
  const detailFrame = geminiFrame ?? annotatedFrame;
  const cooldownActive = cooldownRemaining > 0;
  const hasScanResult = lastScanAt !== null;

  useEffect(() => {
    if (cooldownEndRef.current === 0) return;

    const intervalId = window.setInterval(() => {
      if (cooldownPausedRef.current) return;

      const remaining = Math.max(0, cooldownEndRef.current - Date.now());
      setCooldownRemaining(remaining);

      if (remaining <= 0) {
        cooldownEndRef.current = 0;
        window.clearInterval(intervalId);
      }
    }, 100);

    return () => window.clearInterval(intervalId);
  }, [cooldownActive]);

  const stopCamera = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setCameraActive(false);
    setAutoScan(false);
  }, []);

  const startCamera = useCallback(async () => {
    setError(null);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "environment",
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      setCameraActive(true);
      setDetecciones([]);
      setAnnotatedFrame(null);
      setGeminiFrame(null);
      setLowConfidenceScan(false);
      lastDetectionNameRef.current = null;
    } catch {
      setError(
        "No pudimos acceder a la cámara. Verifica los permisos del navegador.",
      );
    }
  }, []);

  const cancelCooldown = useCallback(() => {
    cooldownEndRef.current = 0;
    cooldownPausedRef.current = false;
    pausedRemainingRef.current = 0;
    setCooldownRemaining(0);
    setCooldownPaused(false);
    setDetecciones([]);
    setGeminiFrame(null);
    lastDetectionNameRef.current = null;
  }, []);

  const togglePauseCooldown = useCallback(() => {
    if (cooldownPaused) {
      cooldownEndRef.current = Date.now() + pausedRemainingRef.current;
      cooldownPausedRef.current = false;
      setCooldownPaused(false);
    } else {
      pausedRemainingRef.current = cooldownEndRef.current - Date.now();
      cooldownEndRef.current = 0;
      cooldownPausedRef.current = true;
      setCooldownPaused(true);
    }
  }, [cooldownPaused]);

  const scanFrame = useCallback(() => {
    if (isBlocked) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas || scanningRef.current || !cameraActive) {
      return;
    }

    scanningRef.current = true;
    setIsScanning(true);
    setError(null);
    setDetecciones([]);
    setAnnotatedFrame(null);
    setGeminiFrame(null);
    setLowConfidenceScan(false);

    const imageBase64 = captureFrame(video, canvas);

    detectImageBase64(imageBase64, true)
      .then((result) => {
        setAnnotatedFrame(
          result.frame_base64 ? `data:image/jpeg;base64,${result.frame_base64}` : null,
        );
        setLastScanAt(
          new Intl.DateTimeFormat("es-CO", {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
          }).format(new Date()),
        );

        const sorted = pickBest(result.detecciones);
        const primary = sorted[0] ?? null;

        if (!primary) {
          setDetecciones([]);
          speakText("No se encontró ningún objeto en cámara.");
          return;
        }

        if (primary.confianza < GEMINI_MIN_CONFIDENCE) {
          setDetecciones([]);
          setLowConfidenceScan(true);
          speakText("La imagen no es lo suficientemente clara. No se pudo clasificar.");
          return;
        }

        if (primary.confianza >= HIGH_CONFIDENCE) {
          setDetecciones(sorted);
          lastDetectionNameRef.current = primary.nombre;
          startCooldown(cooldownEndRef, setCooldownRemaining, COOLDOWN_SECONDS_HIGH, setCooldownDuration);
          const voiceMessage = primary.recomendacion 
            ? `${primary.nombre}. ${primary.recomendacion}`
            : `${primary.nombre}. Depositar en contenedor de color ${primary.color_caja}.`;
          speakText(voiceMessage);
          return;
        }

        lastDetectionNameRef.current = primary.nombre;
        setGeminiFrame(`data:image/jpeg;base64,${imageBase64}`);
        setIsGeminiLoading(true);

        detectImageGemini(imageBase64)
          .then((geminiResult) => {
            if (geminiResult.error) {
              setError(geminiResult.error);
            }
            if(geminiResult.detecciones.length > 0) {
              startCooldown(cooldownEndRef, setCooldownRemaining, COOLDOWN_SECONDS, setCooldownDuration);
              
              // Reproducir instrucciones por voz
              const primary = geminiResult.detecciones[0];
              if (primary.recomendacion) {
                const voiceMessage = `${primary.nombre}. ${primary.recomendacion}`;
                speakText(voiceMessage);
              }
            }
            setDetecciones(pickBest(geminiResult.detecciones));
          })
          .catch((geminiError) => {
            const message =
              geminiError instanceof Error
                ? geminiError.message
                : "Error al clasificar con Gemini.";
            setError(message);
          })
          .finally(() => {
            setIsGeminiLoading(false);
          });
      })
      .catch((scanError) => {
        const message =
          scanError instanceof Error
            ? scanError.message
            : "Ocurrió un error al analizar el frame.";
        setError(message);
      })
      .finally(() => {
        scanningRef.current = false;
        setIsScanning(false);
      });
  }, [cameraActive, isBlocked, autoScan]);

  useEffect(() => {
    return () => stopCamera();
  }, [stopCamera]);

  useEffect(() => {
    if (!cameraActive || !autoScan) {
      return;
    }

    const intervalId = window.setInterval(() => {
      scanFrame();
    }, SCAN_INTERVAL_MS);

    scanFrame();

    return () => window.clearInterval(intervalId);
  }, [autoScan, cameraActive, scanFrame]);

  const primaryDetection = detecciones[0] ?? null;
  const cooldownSecondsLeft = Math.ceil(cooldownRemaining / 1000);
  const cooldownProgress = cooldownRemaining / (cooldownDuration * 1000);

  return (
    <div className="classifier-layout">
      <div className="classifier-panel">
        <div className="camera-preview">
          <div className="camera-grid" />

          {!cameraActive && (
            <div className="camera-content">
              <span className="camera-icon">◉</span>
              <h3>Activa la cámara para comenzar</h3>
              <p>Ubica el residuo en el centro del recuadro.</p>
            </div>
          )}

          <video
            ref={videoRef}
            className={`camera-video ${cameraActive ? "visible" : ""}`}
            playsInline
            muted
            autoPlay
          />

          {detailFrame && (
            <div className="camera-result-badge">
              <img
                src={detailFrame}
                alt="Frame analizado"
                className="camera-result-thumb"
              />
            </div>
          )}

          <div className="camera-corner top-left" />
          <div className="camera-corner top-right" />
          <div className="camera-corner bottom-left" />
          <div className="camera-corner bottom-right" />

          {isScanning && !isGeminiLoading && (
            <div className="scan-overlay">Analizando objeto...</div>
          )}

          {isGeminiLoading && (
            <div className="scan-overlay scan-overlay--gemini">
              Clasificando con Gemini Vision...
            </div>
          )}
        </div>

        <canvas ref={canvasRef} className="hidden-canvas" />

        <div className="classifier-actions">
          {!cameraActive ? (
            <button className="scan-button" type="button" onClick={() => void startCamera()}>
              Activar cámara
            </button>
          ) : (
            <>
              <button
                className="scan-button"
                type="button"
                onClick={scanFrame}
                disabled={isScanning || isBlocked}
              >
                {isGeminiLoading
                  ? "Gemini analizando..."
                  : isBlocked
                    ? `Esperando ${cooldownSecondsLeft}s...`
                    : isScanning
                      ? "Clasificando..."
                      : "Clasificar ahora"}
              </button>

              <button
                className="secondary-button classifier-secondary"
                type="button"
                onClick={() => setAutoScan((value) => !value)}
                disabled={isBlocked}
              >
                {autoScan ? "Pausar escaneo automático" : "Escaneo automático"}
              </button>

              <button
                className="secondary-button classifier-secondary"
                type="button"
                onClick={stopCamera}
              >
                Detener cámara
              </button>
            </>
          )}
        </div>

        {error && (
          <p className="classifier-error" role="alert">
            {error}
          </p>
        )}

        {lastScanAt && (
          <p className="scan-status">
            Último análisis: {lastScanAt}
            {autoScan && !isBlocked ? " · escaneo automático activo" : ""}
          </p>
        )}
      </div>

      <div className={`classifier-detail${primaryDetection ? ` detail-${primaryDetection.color_caja}` : ""}`}>
        <div className="result-card">
          {!hasScanResult ? (
            <div className="detail-empty">
              <span className="detail-empty__icon">◉</span>
              <p>Activa la cámara y escanea un residuo para ver los resultados aquí.</p>
            </div>
          ) : detecciones.length === 0 ? (
            <div className="detail-empty">
              <span className="detail-empty__icon">{isGeminiLoading ? "◌" : "∅"}</span>
              <p>
                {isGeminiLoading
                  ? "Gemini está analizando la imagen..."
                  : lowConfidenceScan
                    ? "La imagen no es suficientemente clara. No se pudo clasificar."
                    : "No se encontró ningún objeto en cámara. Intenta con otro ángulo o acercando el residuo."}
              </p>
            </div>
          ) : (
            <>
              {detailFrame && (
                <div className="detail-image">
                  <img src={detailFrame} alt="Frame analizado" />
                </div>
              )}

              {cooldownRemaining > 0 && (
                <>
                <div className="cooldown-bar">
                  <div
                    className="cooldown-bar__fill"
                    style={{ width: `${cooldownProgress * 100}%` }}
                  />
                  <span className="cooldown-bar__label">
                    {cooldownPaused
                      ? `Pausado en ${cooldownSecondsLeft}s`
                      : `Actualización en ${cooldownSecondsLeft}s`}
                  </span>
                </div>
                <div className="cooldown-bar__actions">
                    <button
                      type="button"
                      className="cooldown-btn"
                      onClick={togglePauseCooldown}
                    >
                      {cooldownPaused ? "Reanudar" : "Pausar"}
                    </button>
                    <button
                      type="button"
                      className="cooldown-btn cooldown-btn--cancel"
                      onClick={cancelCooldown}
                    >
                      Cancelar
                    </button>
                  </div>
                </>
              )}

              <div className="result-title">
                <span className="result-icon">♻</span>
                <div>
                  <span className="eyebrow">
                    {isGeminiLoading
                      ? "ANALIZANDO CON GEMINI"
                      : geminiFrame
                        ? "CLASIFICACIÓN GEMINI"
                        : "RESULTADO EN TIEMPO REAL"}
                  </span>
                  <h2>{primaryDetection!.nombre}</h2>
                </div>
              </div>

              <div className="result-grid">
                <div className="result-grid__item">
                  <span className="result-label">CONTENEDOR</span>
                  <strong
                    className={`bin-badge bin-${primaryDetection!.color_caja}`}
                  >
                    {COLOR_LABEL[primaryDetection!.color_caja]}
                  </strong>
                </div>

                <div className="result-grid__item">
                  <span className="result-label">CATEGORÍA</span>
                  <strong>{primaryDetection!.categoria}</strong>
                </div>

                <div className="result-grid__item">
                  <span className="result-label">CONFIANZA</span>
                  <strong>
                    {geminiFrame
                      ? "Gemini"
                      : `${Math.round(primaryDetection!.confianza * 100)}%`}
                  </strong>
                </div>
              </div>

              {primaryDetection!.recomendacion && (
                <p className="result-message">{primaryDetection!.recomendacion}</p>
              )}

              {detecciones.length > 1 && !geminiFrame && (
                <div className="detection-list">
                  <span className="result-label">TODOS LOS OBJETOS DETECTADOS</span>
                  <ul>
                    {detecciones.map((det) => (
                      <li key={det.id} className={`detection-chip chip-${det.color_caja}`}>
                        <span>{det.nombre}</span>
                        <small>
                          {COLOR_LABEL[det.color_caja]} · {Math.round(det.confianza * 100)}%
                        </small>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      <div className="classifier-guide">
        <h3>Guía de clasificación</h3>
        <p>
          EcoSorter analiza el objeto frente a la cámara y sugiere el contenedor
          según estas categorías:
        </p>

        <ul className="guide-list">
          {GUIA_CLASIFICACION.map((item) => {
            const matching = detecciones.filter((d) => d.color_caja === item.color);
            return (
              <li
                key={item.color}
                className={`guide-item guide-${item.color}${matching.length > 0 ? " guide-active" : ""}`}
              >
                <span className={`guide-swatch swatch-${item.color}`} aria-hidden />
                <div>
                  <strong>{item.etiqueta}</strong>
                  <span>{item.descripcion}</span>
                  <small>{item.ejemplos}</small>
                  {matching.length > 0 && (
                    <div className="guide-detections">
                      {matching.map((det) => (
                        <span key={det.id} className="guide-detection-tag">
                          {det.nombre} ({Math.round(det.confianza * 100)}%)
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}
