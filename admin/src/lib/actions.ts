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

export interface ActionState {
  error?: string;
  success?: boolean;
}

async function runAction(
  path: string,
  options: RequestInit,
  revalidate: string,
): Promise<ActionState> {
  try {
    await backendFetch(path, options);
  } catch (error) {
    unstable_rethrow(error);
    if (error instanceof BackendError) {
      return { error: error.message };
    }
    return { error: "Action impossible" };
  }
  revalidatePath(revalidate);
  return { success: true };
}

// --- cards ---

export async function blockCardAction(cardId: string): Promise<ActionState> {
  return runAction(`/api/v1/admin/cards/${cardId}/block`, { method: "POST" }, "/dashboard/cards");
}

export async function unblockCardAction(cardId: string): Promise<ActionState> {
  return runAction(`/api/v1/admin/cards/${cardId}/unblock`, { method: "POST" }, "/dashboard/cards");
}

// --- FX rates ---

export async function createFxRateAction(
  _prevState: ActionState,
  formData: FormData,
): Promise<ActionState> {
  return runAction(
    "/api/v1/admin/fx-rates",
    {
      method: "POST",
      body: JSON.stringify({
        base_currency: String(formData.get("base_currency") ?? "").toUpperCase(),
        quote_currency: String(formData.get("quote_currency") ?? "").toUpperCase(),
        rate: String(formData.get("rate") ?? ""),
      }),
    },
    "/dashboard/fx",
  );
}

// --- limits ---

export async function createLimitRuleAction(
  _prevState: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const countryCode = String(formData.get("country_code") ?? "").trim();
  const kycLevel = String(formData.get("kyc_level") ?? "").trim();
  const maxAmount = String(formData.get("max_amount") ?? "").trim();
  const maxCount = String(formData.get("max_count") ?? "").trim();

  return runAction(
    "/api/v1/admin/limits",
    {
      method: "POST",
      body: JSON.stringify({
        limit_type: String(formData.get("limit_type") ?? ""),
        country_code: countryCode || null,
        kyc_level: kycLevel ? Number(kycLevel) : null,
        max_amount: maxAmount || null,
        max_count: maxCount ? Number(maxCount) : null,
      }),
    },
    "/dashboard/limits",
  );
}

export async function deactivateLimitRuleAction(ruleId: string): Promise<ActionState> {
  return runAction(
    `/api/v1/admin/limits/${ruleId}/deactivate`,
    { method: "POST" },
    "/dashboard/limits",
  );
}

// --- fees ---

export async function createFeeRuleAction(
  _prevState: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const countryCode = String(formData.get("country_code") ?? "").trim();
  const providerName = String(formData.get("provider_name") ?? "").trim();
  const kycLevel = String(formData.get("kyc_level") ?? "").trim();
  const rate = String(formData.get("rate") ?? "").trim();
  const fixedAmount = String(formData.get("fixed_amount") ?? "").trim();

  return runAction(
    "/api/v1/admin/fees",
    {
      method: "POST",
      body: JSON.stringify({
        fee_type: String(formData.get("fee_type") ?? ""),
        country_code: countryCode || null,
        provider_name: providerName || null,
        kyc_level: kycLevel ? Number(kycLevel) : null,
        rate: rate || null,
        fixed_amount: fixedAmount || null,
      }),
    },
    "/dashboard/fees",
  );
}

export async function deactivateFeeRuleAction(ruleId: string): Promise<ActionState> {
  return runAction(
    `/api/v1/admin/fees/${ruleId}/deactivate`,
    { method: "POST" },
    "/dashboard/fees",
  );
}

// --- admin accounts ---

export async function createAdminAccountAction(
  _prevState: ActionState,
  formData: FormData,
): Promise<ActionState> {
  return runAction(
    "/api/v1/admin/accounts",
    {
      method: "POST",
      body: JSON.stringify({
        email: String(formData.get("email") ?? ""),
        password: String(formData.get("password") ?? ""),
        role: String(formData.get("role") ?? ""),
      }),
    },
    "/dashboard/accounts",
  );
}

export async function updateAdminRoleAction(adminId: string, role: string): Promise<ActionState> {
  return runAction(
    `/api/v1/admin/accounts/${adminId}/role`,
    { method: "POST", body: JSON.stringify({ role }) },
    "/dashboard/accounts",
  );
}

export async function setAdminActiveAction(
  adminId: string,
  isActive: boolean,
): Promise<ActionState> {
  return runAction(
    `/api/v1/admin/accounts/${adminId}/active`,
    { method: "POST", body: JSON.stringify({ is_active: isActive }) },
    "/dashboard/accounts",
  );
}

// --- compliance ---

export async function resolveComplianceAlertAction(
  alertId: string,
  notes: string,
): Promise<ActionState> {
  return runAction(
    `/api/v1/admin/compliance/alerts/${alertId}/resolve`,
    { method: "POST", body: JSON.stringify({ resolution_notes: notes || null }) },
    "/dashboard/compliance",
  );
}

export async function dismissComplianceAlertAction(
  alertId: string,
  notes: string,
): Promise<ActionState> {
  return runAction(
    `/api/v1/admin/compliance/alerts/${alertId}/dismiss`,
    { method: "POST", body: JSON.stringify({ resolution_notes: notes || null }) },
    "/dashboard/compliance",
  );
}

export async function unfreezeUserAction(userId: string): Promise<ActionState> {
  return runAction(
    `/api/v1/admin/compliance/users/${userId}/unfreeze`,
    { method: "POST" },
    "/dashboard/compliance",
  );
}

// --- support ---

export async function replySupportTicketAction(
  ticketId: string,
  body: string,
): Promise<ActionState> {
  if (!body.trim()) {
    return { error: "Le message ne peut pas être vide" };
  }
  return runAction(
    `/api/v1/admin/support/tickets/${ticketId}/messages`,
    { method: "POST", body: JSON.stringify({ body }) },
    `/dashboard/support/${ticketId}`,
  );
}

export async function resolveSupportTicketAction(ticketId: string): Promise<ActionState> {
  return runAction(
    `/api/v1/admin/support/tickets/${ticketId}/resolve`,
    { method: "POST" },
    `/dashboard/support/${ticketId}`,
  );
}

export async function closeSupportTicketAction(ticketId: string): Promise<ActionState> {
  return runAction(
    `/api/v1/admin/support/tickets/${ticketId}/close`,
    { method: "POST" },
    `/dashboard/support/${ticketId}`,
  );
}
