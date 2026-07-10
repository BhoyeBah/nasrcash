"use client";

import { useActionState } from "react";

import { createFeeRuleAction, type ActionState } from "@/lib/actions";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const initialState: ActionState = {};

const FEE_TYPES = ["topup", "withdrawal", "payment"];

export function CreateFeeRuleForm() {
  const [state, formAction, pending] = useActionState(createFeeRuleAction, initialState);

  return (
    <form action={formAction} className="flex flex-wrap items-end gap-3">
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="fee_type">Type</Label>
        <select
          id="fee_type"
          name="fee_type"
          required
          className="h-9 rounded-md border border-border bg-card px-3 text-sm"
        >
          {FEE_TYPES.map((type) => (
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
        <Label htmlFor="provider_name">Provider (optionnel)</Label>
        <Input id="provider_name" name="provider_name" placeholder="orange_money" className="w-40" />
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="kyc_level">Niveau KYC (optionnel)</Label>
        <Input id="kyc_level" name="kyc_level" type="number" min="0" max="2" className="w-24" />
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="rate">Taux (ex: 0.02)</Label>
        <Input id="rate" name="rate" type="number" step="any" min="0" className="w-32" />
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="fixed_amount">Montant fixe</Label>
        <Input id="fixed_amount" name="fixed_amount" type="number" step="any" min="0" className="w-32" />
      </div>
      <Button type="submit" disabled={pending}>
        {pending ? "Ajout..." : "Ajouter"}
      </Button>
      {state.error && <p className="w-full text-sm text-destructive">{state.error}</p>}
    </form>
  );
}
