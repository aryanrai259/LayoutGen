/**
 * Floor Plan API Client
 * Handles both streaming and direct generation endpoints
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export async function generateDirect(payload) {
  const url = `${API_BASE_URL}/floor_plan/generate`;

  console.log("Direct API Request →", url);

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API Error ${response.status}: ${errorText}`);
  }

  return response.json();
}

export async function generateStream(payload, handlers, abortSignal) {
  const url = `${API_BASE_URL}/floor_plan/generate/stream`;

  console.log("Streaming API Request →", url);

  const { onProgress, onSvg, onFinal, onError } = handlers;

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
      },
      body: JSON.stringify(payload),
      signal: abortSignal
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API Error ${response.status}: ${errorText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let buffer = "";
    let currentEvent = null;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmed = line.trim();

        if (!trimmed) {
          currentEvent = null;
          continue;
        }

        if (trimmed.startsWith("event:")) {
          currentEvent = trimmed.substring(6).trim();
        }

        if (trimmed.startsWith("data:")) {
          const jsonStr = trimmed.substring(5).trim();
          try {
            const parsed = JSON.parse(jsonStr);

            if (currentEvent === "progress") onProgress?.(parsed);
            if (currentEvent === "svg") onSvg?.(parsed);
            if (currentEvent === "final_response") onFinal?.(parsed);

          } catch (err) {
            console.warn("SSE Parse Error:", err);
          }
        }
      }
    }

  } catch (error) {
    if (error.name === "AbortError") {
      console.log("Streaming aborted by user");
      return;
    }

    console.error("Streaming failed:", error);
    onError?.(error);
  }
}
