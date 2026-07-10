import { StatusBadge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TicketReplyForm } from "@/components/ticket-reply-form";
import { TicketActions } from "@/components/ticket-actions";
import { backendFetch } from "@/lib/backend";
import { formatDate } from "@/lib/utils";
import type { SupportTicketDetail } from "@/lib/types";

export default async function SupportTicketPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const detail = await backendFetch<SupportTicketDetail>(`/api/v1/admin/support/tickets/${id}`);
  const { ticket, messages } = detail;
  const isClosed = ticket.status === "resolved" || ticket.status === "closed";

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">{ticket.subject}</h1>
          <p className="text-sm text-muted-foreground">
            {ticket.category} · <span className="font-mono">{ticket.user_id}</span>
          </p>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge status={ticket.status} />
          {!isClosed && <TicketActions ticketId={ticket.id} />}
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-foreground">Conversation</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`rounded-md border border-border p-3 text-sm ${
                message.sender_type === "admin" ? "bg-accent/40" : "bg-muted/40"
              }`}
            >
              <div className="mb-1 flex items-center justify-between text-xs text-muted-foreground">
                <span>{message.sender_type === "admin" ? "Support" : "Client"}</span>
                <span>{formatDate(message.created_at)}</span>
              </div>
              <p>{message.body}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      {!isClosed && <TicketReplyForm ticketId={ticket.id} />}
    </div>
  );
}
