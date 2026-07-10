"use client";

import { useState, useTransition } from "react";

import { replySupportTicketAction } from "@/lib/actions";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function TicketReplyForm({ ticketId }: { ticketId: string }) {
  const [body, setBody] = useState("");
  const [error, setError] = useState<string | undefined>();
  const [isPending, startTransition] = useTransition();

  function handleSend() {
    setError(undefined);
    startTransition(async () => {
      const result = await replySupportTicketAction(ticketId, body);
      if (result.error) {
        setError(result.error);
      } else {
        setBody("");
      }
    });
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-foreground">Répondre</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <textarea
          value={body}
          onChange={(e) => setBody(e.target.value)}
          placeholder="Votre réponse..."
          rows={4}
          className="w-full rounded-md border border-border bg-card p-3 text-sm"
        />
        {error && <p className="text-sm text-destructive">{error}</p>}
        <div>
          <Button disabled={isPending || !body.trim()} onClick={handleSend}>
            {isPending ? "Envoi..." : "Envoyer"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
