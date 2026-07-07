"use client";

import { useState, useTransition } from "react";

import { approveKycAction, rejectKycAction } from "@/lib/actions";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function KycActions({ profileId }: { profileId: string }) {
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | undefined>();
  const [showReject, setShowReject] = useState(false);
  const [reason, setReason] = useState("");
  const [done, setDone] = useState(false);

  if (done) {
    return <span className="text-sm text-muted-foreground">Traité</span>;
  }

  function handleApprove() {
    setError(undefined);
    startTransition(async () => {
      const result = await approveKycAction(profileId);
      if (result.error) {
        setError(result.error);
      } else {
        setDone(true);
      }
    });
  }

  function handleReject() {
    setError(undefined);
    startTransition(async () => {
      const result = await rejectKycAction(profileId, reason);
      if (result.error) {
        setError(result.error);
      } else {
        setDone(true);
      }
    });
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="flex gap-2">
        <Button size="sm" disabled={isPending} onClick={handleApprove}>
          Approuver
        </Button>
        <Button
          size="sm"
          variant="outline"
          disabled={isPending}
          onClick={() => setShowReject((v) => !v)}
        >
          Rejeter
        </Button>
      </div>
      {showReject && (
        <div className="flex gap-2">
          <Input
            placeholder="Motif du rejet"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className="h-8 text-xs"
          />
          <Button size="sm" variant="destructive" disabled={isPending} onClick={handleReject}>
            Confirmer
          </Button>
        </div>
      )}
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}
