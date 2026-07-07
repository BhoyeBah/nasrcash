"use server";

import { cookies } from "next/headers";
import { redirect, unstable_rethrow } from "next/navigation";
import { revalidatePath } from "next/cache";

import { backendFetch, backendLogin, BackendError } from "@/lib/backend";
import { ADMIN_TOKEN_COOKIE, getAdminToken } from "@/lib/session";

export interface LoginState {
  error?: string;
}

export async function loginAction(
  _prevState: LoginState,
  formData: FormData,
): Promise<LoginState> {
  const email = String(formData.get("email") ?? "");
  const password = String(formData.get("password") ?? "");

  if (!email || !password) {
    return { error: "Email et mot de passe requis" };
  }

  try {
    const { access_token } = await backendLogin(email, password);
    const cookieStore = await cookies();
    cookieStore.set(ADMIN_TOKEN_COOKIE, access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 15, // matches backend admin access token lifetime
    });
  } catch (error) {
    if (error instanceof BackendError) {
      return { error: error.message };
    }
    return { error: "Connexion au serveur impossible" };
  }

  redirect("/dashboard");
}

export async function logoutAction() {
  const cookieStore = await cookies();
  cookieStore.delete(ADMIN_TOKEN_COOKIE);
  redirect("/login");
}

export interface KycActionState {
  error?: string;
  success?: boolean;
}

export async function approveKycAction(
  profileId: string,
): Promise<KycActionState> {
  const token = await getAdminToken();
  if (!token) redirect("/login");

  try {
    await backendFetch(`/api/v1/admin/kyc/${profileId}/approve`, {
      method: "POST",
    });
  } catch (error) {
    unstable_rethrow(error);
    if (error instanceof BackendError) {
      return { error: error.message };
    }
    return { error: "Impossible d'approuver ce dossier KYC" };
  }

  revalidatePath("/kyc");
  return { success: true };
}

export async function rejectKycAction(
  profileId: string,
  reason: string,
): Promise<KycActionState> {
  if (!reason.trim()) {
    return { error: "Un motif de rejet est requis" };
  }

  try {
    await backendFetch(`/api/v1/admin/kyc/${profileId}/reject`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    });
  } catch (error) {
    unstable_rethrow(error);
    if (error instanceof BackendError) {
      return { error: error.message };
    }
    return { error: "Impossible de rejeter ce dossier KYC" };
  }

  revalidatePath("/kyc");
  return { success: true };
}
