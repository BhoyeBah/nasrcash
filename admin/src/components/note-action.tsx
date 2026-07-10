"use client";

import { useState, useTransition } from "react";

import { Button, type ButtonProps } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { ActionState } from "@/lib/actions";

/** A button that reveals a note field before confirming — used for actions
 * that want an optional/required free-text justification (resolve, dismiss). */
export function NoteAction({
  action,
  label,
  variant,
  placeholder = "Note (optionnel)",
}: {
  action: (notes: string) => Promise<ActionState>;
  label: string;
  variant?: ButtonProps["variant"];
  placeholder?: string;
}) {
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | undefined>();
  const [expanded, setExpanded] = useState(false);
  const [notes, setNotes] = useState("");
  const [done, setDone] = useState(false);

  if (done) {
    return <span className="text-xs text-muted-foreground">Fait</span>;
  }

  if (!expanded) {
    return (
      <Button size="sm" variant={variant} onClick={() => setExpanded(true)}>
        {label}
      </Button>
    );
  }

  function handleConfirm() {
    setError(undefined);
    startTransition(async () => {
      const result = await action(notes);
      if (result.error) {
        setError(result.error);
      } else {
        setDone(true);
      }
    });
  }

  return (
    <div className="flex flex-col gap-1">
      <div className="flex gap-2">
        <Input
          placeholder={placeholder}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          className="h-8 text-xs"
        />
        <Button size="sm" variant={variant} disabled={isPending} onClick={handleConfirm}>
          Confirmer
        </Button>
      </div>
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}
