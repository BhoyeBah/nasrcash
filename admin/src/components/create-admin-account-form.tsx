"use client";

import { useActionState } from "react";

import { createAdminAccountAction, type ActionState } from "@/lib/actions";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const initialState: ActionState = {};

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

export function CreateAdminAccountForm() {
  const [state, formAction, pending] = useActionState(createAdminAccountAction, initialState);

  return (
    <form action={formAction} className="flex flex-wrap items-end gap-3">
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="email">Email</Label>
        <Input id="email" name="email" type="email" required className="w-56" />
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="password">Mot de passe</Label>
        <Input id="password" name="password" type="password" required className="w-48" />
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="role">Rôle</Label>
        <select
          id="role"
          name="role"
          required
          className="h-9 rounded-md border border-border bg-card px-3 text-sm"
        >
          {ADMIN_ROLES.map((role) => (
            <option key={role} value={role}>
              {role}
            </option>
          ))}
        </select>
      </div>
      <Button type="submit" disabled={pending}>
        {pending ? "Création..." : "Créer"}
      </Button>
      {state.error && <p className="w-full text-sm text-destructive">{state.error}</p>}
    </form>
  );
}
