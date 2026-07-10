import Link from "next/link";

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { StatusBadge } from "@/components/ui/badge";
import { backendFetch } from "@/lib/backend";
import { formatDate } from "@/lib/utils";
import type { SupportTicket } from "@/lib/types";

export default async function SupportPage({
  searchParams,
}: {
  searchParams: Promise<{ status?: string }>;
}) {
  const params = await searchParams;
  const query = new URLSearchParams();
  if (params.status) query.set("status", params.status);

  const tickets = await backendFetch<SupportTicket[]>(
    `/api/v1/admin/support/tickets?${query.toString()}`,
  );

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Support client</h1>
        <p className="text-sm text-muted-foreground">{tickets.length} ticket(s)</p>
      </div>

      <form className="flex gap-3">
        <select
          name="status"
          defaultValue={params.status ?? ""}
          className="h-9 rounded-md border border-border bg-card px-3 text-sm"
        >
          <option value="">Tous les statuts</option>
          <option value="open">Ouvert</option>
          <option value="in_progress">En cours</option>
          <option value="resolved">Résolu</option>
          <option value="closed">Fermé</option>
        </select>
        <button
          type="submit"
          className="h-9 rounded-md border border-border px-4 text-sm hover:bg-muted"
        >
          Filtrer
        </button>
      </form>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Sujet</TableHead>
            <TableHead>Catégorie</TableHead>
            <TableHead>Utilisateur</TableHead>
            <TableHead>Statut</TableHead>
            <TableHead>Créé le</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {tickets.map((ticket) => (
            <TableRow key={ticket.id}>
              <TableCell className="font-medium">
                <Link href={`/dashboard/support/${ticket.id}`} className="hover:underline">
                  {ticket.subject}
                </Link>
              </TableCell>
              <TableCell>{ticket.category}</TableCell>
              <TableCell className="font-mono text-xs">{ticket.user_id}</TableCell>
              <TableCell>
                <StatusBadge status={ticket.status} />
              </TableCell>
              <TableCell className="text-muted-foreground">{formatDate(ticket.created_at)}</TableCell>
            </TableRow>
          ))}
          {tickets.length === 0 && (
            <TableRow>
              <TableCell colSpan={5} className="text-center text-muted-foreground">
                Aucun ticket
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
