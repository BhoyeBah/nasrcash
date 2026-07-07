import { cookies } from "next/headers";

export const ADMIN_TOKEN_COOKIE = "nasrcash_admin_token";

export async function getAdminToken(): Promise<string | undefined> {
  const cookieStore = await cookies();
  return cookieStore.get(ADMIN_TOKEN_COOKIE)?.value;
}
