"use client";

import { useState, useTransition } from "react";

import { Button, type ButtonProps } from "@/components/ui/button";
import type { ActionState } from "@/lib/actions";

/** A single button that runs a no-argument server action and surfaces its error inline. */
export function ActionButton({
  action,
  label,
  pendingLabel,
  variant,
}: {
  action: () => Promise<ActionState>;
  label: string;
  pendingLabel?: string;
  variant?: ButtonProps["variant"];
}) {
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | undefined>();
  const [done, setDone] = useState(false);

  function handleClick() {
    setError(undefined);
    startTransition(async () => {
      const result = await action();
      if (result.error) {
        setError(result.error);
      } else {
        setDone(true);
      }
    });
  }

  return (
    <div className="flex flex-col gap-1">
      <Button size="sm" variant={variant} disabled={isPending || done} onClick={handleClick}>
        {isPending ? (pendingLabel ?? label) : label}
      </Button>
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}
