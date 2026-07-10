"use client";

import { useActionState } from "react";

import { createLimitRuleAction, type ActionState } from "@/lib/actions";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const initialState: ActionState = {};

const LIMIT_TYPES = [
  "topup_min",
  "topup_max",
  "wallet_daily_topup_cap",
  "withdrawal_daily_cap",
  "card_payment_daily_cap",
  "max_cards_per_user",
];

export function CreateLimitRuleForm() {
  const [state, formAction, pending] = useActionState(createLimitRuleAction, initialState);

  return (
    <form action={formAction} className="flex flex-wrap items-end gap-3">
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="limit_type">Type</Label>
        <select
          id="limit_type"
          name="limit_type"
          required
          className="h-9 rounded-md border border-border bg-card px-3 text-sm"
        >
          {LIMIT_TYPES.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="country_code">Pays (optionnel)</Label>
        <Input id="country_code" name="country_code" placeholder="GN" maxLength={2} className="w-20 uppercase" />
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="kyc_level">Niveau KYC (optionnel)</Label>
        <Input id="kyc_level" name="kyc_level" type="number" min="0" max="2" className="w-24" />
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="max_amount">Montant max</Label>
        <Input id="max_amount" name="max_amount" type="number" step="any" min="0" className="w-40" />
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="max_count">Nombre max</Label>
        <Input id="max_count" name="max_count" type="number" min="0" className="w-32" />
      </div>
      <Button type="submit" disabled={pending}>
        {pending ? "Ajout..." : "Ajouter"}
      </Button>
      {state.error && <p className="w-full text-sm text-destructive">{state.error}</p>}
    </form>
  );
}
