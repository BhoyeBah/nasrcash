"use client";

import { ActionButton } from "@/components/action-button";
import { resolveSupportTicketAction, closeSupportTicketAction } from "@/lib/actions";

export function TicketActions({ ticketId }: { ticketId: string }) {
  return (
    <div className="flex gap-2">
      <ActionButton label="Marquer résolu" action={() => resolveSupportTicketAction(ticketId)} />
      <ActionButton
        label="Fermer"
        variant="outline"
        action={() => closeSupportTicketAction(ticketId)}
      />
    </div>
  );
}
