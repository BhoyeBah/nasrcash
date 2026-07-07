import { redirect } from "next/navigation";

import { getAdminToken } from "@/lib/session";

const BACKEND_URL = process.env.NASRCASH_API_URL ?? "http://localhost:8000";

export class BackendError extends Error {
  constructor(
    public status: number,
    public errorCode: string,
    message: string,
  ) {
    super(message);
  }
}

/**
 * Server-side only fetch against the NasrCash FastAPI backend, authenticated
 * with the admin's JWT (read from the httpOnly cookie — never exposed to
 * client JS). A 401 here means the token is missing/expired/invalid; we
 * redirect to /login rather than let a Server Component render with no data.
 */
export async function backendFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = await getAdminToken();
  if (!token) {
    redirect("/login");
  }

  const response = await fetch(`${BACKEND_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
    cache: "no-store",
  });

  if (response.status === 401) {
    redirect("/login");
  }

  const body = await response.json().catch(() => null);

  if (!response.ok) {
    throw new BackendError(
      response.status,
      body?.error_code ?? "unknown_error",
      body?.message ?? "Une erreur est survenue",
    );
  }

  return body as T;
}

export async function backendLogin(email: string, password: string) {
  const response = await fetch(`${BACKEND_URL}/api/v1/admin/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
    cache: "no-store",
  });

  const body = await response.json().catch(() => null);

  if (!response.ok) {
    throw new BackendError(
      response.status,
      body?.error_code ?? "unknown_error",
      body?.message ?? "Email ou mot de passe invalide",
    );
  }

  return body as { access_token: string; token_type: string };
}
