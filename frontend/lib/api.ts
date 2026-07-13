import type { DeteccionResponse } from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export async function detectImageBase64(
  imageBase64: string,
  includeFrame = true,
): Promise<DeteccionResponse> {
  const response = await fetch(
    `${API_BASE}/detect/image?include_frame=${includeFrame}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image_base64: imageBase64 }),
    },
  );

  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    const message =
      typeof detail?.detail === "string"
        ? detail.detail
        : "No se pudo conectar con el servicio de detección.";
    throw new Error(message);
  }

  return response.json();
}

export async function detectImageGemini(
  imageBase64: string,
): Promise<DeteccionResponse> {
  const response = await fetch(`${API_BASE}/detect/gemini`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image_base64: imageBase64 }),
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    const message =
      typeof detail?.detail === "string"
        ? detail.detail
        : "No se pudo conectar con el servicio de Gemini.";
    throw new Error(message);
  }

  return response.json();
}
