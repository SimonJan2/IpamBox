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
    let fields: Record<string, string> | undefined;
    try {
      const body = await res.json();
      if (body.detail && typeof body.detail === "object") {
        // per-field validation errors, e.g. {"scan_networks": "invalid CIDR"}
        fields = body.detail as Record<string, string>;
        detail = Object.entries(fields)
          .map(([k, v]) => `${k}: ${v}`)
          .join("; ");
      } else {
        detail = body.detail ?? JSON.stringify(body);
      }
    } catch {
      /* keep statusText */
    }
    const err = new Error(`${res.status}: ${detail}`);
    (err as Error & { fields?: Record<string, string> }).fields = fields;
    throw err;
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
  // Raw file body (a File is a Blob/BodyInit) — used by backup restore (.gz)
  // and workbook import (.xlsx -> application/octet-stream).
  upload: <T>(path: string, file: File, contentType = "application/gzip") =>
    req<T>(path, {
      method: "POST",
      body: file,
      headers: { "content-type": contentType },
    }),
  patch: <T>(path: string, body: unknown) =>
    req<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
  del: (path: string) => req<void>(path, { method: "DELETE" }),
};

export const scanStreamUrl = (id: number) => `${API}/api/v1/scans/${id}/stream`;
