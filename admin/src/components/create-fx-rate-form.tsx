"use client";

import { useActionState } from "react";

import { createFxRateAction, type ActionState } from "@/lib/actions";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const initialState: ActionState = {};

export function CreateFxRateForm() {
  const [state, formAction, pending] = useActionState(createFxRateAction, initialState);

  return (
    <form action={formAction} className="flex flex-wrap items-end gap-3">
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="base_currency">Devise de base</Label>
        <Input id="base_currency" name="base_currency" placeholder="USD" maxLength={3} required className="w-24 uppercase" />
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="quote_currency">Devise cible</Label>
        <Input id="quote_currency" name="quote_currency" placeholder="GNF" maxLength={3} required className="w-24 uppercase" />
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="rate">Taux (1 base = X cible)</Label>
        <Input id="rate" name="rate" type="number" step="any" min="0" required className="w-36" />
      </div>
      <Button type="submit" disabled={pending}>
        {pending ? "Ajout..." : "Ajouter"}
      </Button>
      {state.error && <p className="w-full text-sm text-destructive">{state.error}</p>}
    </form>
  );
}
