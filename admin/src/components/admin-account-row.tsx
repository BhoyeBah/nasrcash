"use client";

import { useState, useTransition } from "react";

import { setAdminActiveAction, updateAdminRoleAction } from "@/lib/actions";
import { Button } from "@/components/ui/button";
import type { AdminAccount } from "@/lib/types";

const ADMIN_ROLES = [
  "super_admin",
  "country_admin",
  "compliance_officer",
  "finance_manager",
  "risk_analyst",
  "support_agent",
  "operations_agent",
  "auditor",
  "developer_admin",
];

export function AdminAccountRow({ account }: { account: AdminAccount }) {
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | undefined>();
  const [role, setRole] = useState(account.role);

  function handleRoleChange(newRole: string) {
    setRole(newRole);
    setError(undefined);
    startTransition(async () => {
      const result = await updateAdminRoleAction(account.id, newRole);
      if (result.error) setError(result.error);
    });
  }

  function handleToggleActive() {
    setError(undefined);
    startTransition(async () => {
      const result = await setAdminActiveAction(account.id, !account.is_active);
      if (result.error) setError(result.error);
    });
  }

  return (
    <div className="flex flex-col gap-1">
      <div className="flex gap-2">
        <select
          value={role}
          disabled={isPending}
          onChange={(e) => handleRoleChange(e.target.value)}
          className="h-8 rounded-md border border-border bg-card px-2 text-xs"
        >
          {ADMIN_ROLES.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
        <Button
          size="sm"
          variant={account.is_active ? "destructive" : "outline"}
          disabled={isPending}
          onClick={handleToggleActive}
        >
          {account.is_active ? "Désactiver" : "Réactiver"}
        </Button>
      </div>
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}
