"use client";

import { useState, useTransition } from "react";

import { unfreezeUserAction } from "@/lib/actions";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { RiskScore } from "@/lib/types";

export function RiskScoreLookup() {
  const [userId, setUserId] = useState("");
  const [score, setScore] = useState<RiskScore | null>(null);
  const [error, setError] = useState<string | undefined>();
  const [isPending, startTransition] = useTransition();
  const [unfreezeMessage, setUnfreezeMessage] = useState<string | undefined>();

  function handleLookup() {
    setError(undefined);
    setUnfreezeMessage(undefined);
    startTransition(async () => {
      const response = await fetch(`/api/admin/compliance/risk-score?userId=${userId}`);
      const body = await response.json();
      if (!response.ok) {
        setError(body.message ?? "Introuvable");
        setScore(null);
        return;
      }
      setScore(body);
    });
  }

  function handleUnfreeze() {
    if (!userId) return;
    startTransition(async () => {
      const result = await unfreezeUserAction(userId);
      setUnfreezeMessage(result.error ?? "Compte débloqué.");
    });
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex gap-2">
        <Input
          placeholder="ID utilisateur"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          className="w-96 font-mono text-xs"
        />
        <Button size="sm" disabled={isPending || !userId} onClick={handleLookup}>
          Voir le score de risque
        </Button>
        <Button size="sm" variant="outline" disabled={isPending || !userId} onClick={handleUnfreeze}>
          Débloquer ce compte
        </Button>
      </div>
      {error && <p className="text-xs text-destructive">{error}</p>}
      {unfreezeMessage && <p className="text-xs text-muted-foreground">{unfreezeMessage}</p>}
      {score && (
        <div className="rounded-md border border-border bg-muted/40 p-3 text-sm">
          <p>
            Score : <span className="font-semibold">{score.score}</span> sur{" "}
            {score.window_days} jours ({score.alert_count} alerte(s) ouverte(s))
          </p>
          <p className="text-xs text-muted-foreground">
            {Object.entries(score.breakdown)
              .map(([severity, count]) => `${severity}: ${count}`)
              .join(", ") || "aucune alerte ouverte"}
          </p>
        </div>
      )}
    </div>
  );
}
