// Same-origin by default: Next.js rewrites /api/* to the api service, so the
// app works regardless of which host/port the browser reaches it on.
// Set NEXT_PUBLIC_API_URL only to point the browser directly at the API.
const API = process.env.NEXT_PUBLIC_API_URL ?? "";

const AUTH_PAGES = ["/login", "/setup"];

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    ...init,
    credentials: "include",
    headers: { "content-type": "application/json", ...(init?.headers ?? {}) },
  });
  if (res.status === 401 && !path.startsWith("/api/v1/auth")) {
    if (typeof window !== "undefined" && !AUTH_PAGES.includes(window.location.pathname)) {
      window.location.assign("/login");
    }
  }
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? JSON.stringify(body);
    } catch {
      /* keep statusText */
    }
    throw new Error(`${res.status}: ${detail}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  get: <T>(path: string) => req<T>(path),
  post: <T>(path: string, body?: unknown) =>
    req<T>(path, { method: "POST", body: JSON.stringify(body ?? {}) }),
  postRaw: <T>(path: string, body: BodyInit, contentType = "text/csv") =>
    req<T>(path, {
      method: "POST",
      body,
      headers: { "content-type": contentType },
    }),
  patch: <T>(path: string, body: unknown) =>
    req<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
  del: (path: string) => req<void>(path, { method: "DELETE" }),
};

export const scanStreamUrl = (id: number) => `${API}/api/v1/scans/${id}/stream`;
