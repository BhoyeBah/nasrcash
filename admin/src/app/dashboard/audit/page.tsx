import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { backendFetch } from "@/lib/backend";
import { formatDate } from "@/lib/utils";
import type { AuditLogItem } from "@/lib/types";

export default async function AuditPage({
  searchParams,
}: {
  searchParams: Promise<{ actor_type?: string; action?: string }>;
}) {
  const params = await searchParams;
  const query = new URLSearchParams({ limit: "100" });
  if (params.actor_type) query.set("actor_type", params.actor_type);
  if (params.action) query.set("action", params.action);

  const logs = await backendFetch<AuditLogItem[]>(`/api/v1/admin/audit-logs?${query.toString()}`);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Journal d&apos;audit</h1>
        <p className="text-sm text-muted-foreground">
          {logs.length} entrée(s) — journal append-only de toutes les actions sensibles
        </p>
      </div>

      <form className="flex gap-3">
        <select
          name="actor_type"
          defaultValue={params.actor_type ?? ""}
          className="h-9 rounded-md border border-border bg-card px-3 text-sm"
        >
          <option value="">Tous les acteurs</option>
          <option value="user">Utilisateur</option>
          <option value="admin">Admin</option>
          <option value="system">Système</option>
        </select>
        <input
          name="action"
          defaultValue={params.action ?? ""}
          placeholder="Filtrer par action (ex: card.admin_blocked)"
          className="h-9 w-80 rounded-md border border-border bg-card px-3 text-sm"
        />
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
            <TableHead>Acteur</TableHead>
            <TableHead>Action</TableHead>
            <TableHead>Cible</TableHead>
            <TableHead>Contexte</TableHead>
            <TableHead>Date</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {logs.map((log) => (
            <TableRow key={log.id}>
              <TableCell className="text-xs">
                {log.actor_type}
                {log.actor_id && <span className="font-mono text-muted-foreground"> · {log.actor_id.slice(0, 8)}</span>}
              </TableCell>
              <TableCell className="font-medium">{log.action}</TableCell>
              <TableCell className="text-xs text-muted-foreground">
                {log.target_type ? `${log.target_type}:${log.target_id}` : "—"}
              </TableCell>
              <TableCell className="max-w-xs truncate font-mono text-xs text-muted-foreground">
                {JSON.stringify(log.context)}
              </TableCell>
              <TableCell className="text-muted-foreground">{formatDate(log.created_at)}</TableCell>
            </TableRow>
          ))}
          {logs.length === 0 && (
            <TableRow>
              <TableCell colSpan={5} className="text-center text-muted-foreground">
                Aucune entrée d&apos;audit
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
