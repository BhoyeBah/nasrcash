import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge, StatusBadge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { NoteAction } from "@/components/note-action";
import { RiskScoreLookup } from "@/components/risk-score-lookup";
import { backendFetch } from "@/lib/backend";
import { resolveComplianceAlertAction, dismissComplianceAlertAction } from "@/lib/actions";
import { formatDate } from "@/lib/utils";
import type { ComplianceAlert } from "@/lib/types";

const SEVERITY_VARIANT: Record<string, "outline" | "warning" | "destructive"> = {
  low: "outline",
  medium: "warning",
  high: "destructive",
  critical: "destructive",
};

export default async function CompliancePage({
  searchParams,
}: {
  searchParams: Promise<{ status?: string }>;
}) {
  const params = await searchParams;
  const query = new URLSearchParams();
  if (params.status) query.set("status", params.status);

  const alerts = await backendFetch<ComplianceAlert[]>(
    `/api/v1/admin/compliance/alerts?${query.toString()}`,
  );

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Conformité &amp; risque</h1>
        <p className="text-sm text-muted-foreground">
          {alerts.length} alerte(s) — transactions importantes, vélocité, tentatives de dépassement
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-foreground">Score de risque / débloquer un compte</CardTitle>
        </CardHeader>
        <CardContent>
          <RiskScoreLookup />
        </CardContent>
      </Card>

      <div className="flex items-center justify-between">
        <form className="flex gap-3">
          <select
            name="status"
            defaultValue={params.status ?? ""}
            className="h-9 rounded-md border border-border bg-card px-3 text-sm"
          >
            <option value="">Tous les statuts</option>
            <option value="open">Ouvert</option>
            <option value="reviewing">En revue</option>
            <option value="resolved">Résolu</option>
            <option value="dismissed">Rejeté</option>
          </select>
          <button
            type="submit"
            className="h-9 rounded-md border border-border px-4 text-sm hover:bg-muted"
          >
            Filtrer
          </button>
        </form>
        <a
          href="/api/admin/compliance/report"
          className="inline-flex h-9 items-center justify-center rounded-md border border-border px-4 text-sm hover:bg-muted"
        >
          Exporter le rapport CSV
        </a>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Utilisateur</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Sévérité</TableHead>
            <TableHead>Statut</TableHead>
            <TableHead>Créée le</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {alerts.map((alert) => (
            <TableRow key={alert.id}>
              <TableCell className="font-mono text-xs">{alert.user_id}</TableCell>
              <TableCell className="font-medium">{alert.alert_type}</TableCell>
              <TableCell>
                <Badge variant={SEVERITY_VARIANT[alert.severity] ?? "outline"}>{alert.severity}</Badge>
              </TableCell>
              <TableCell>
                <StatusBadge status={alert.status} />
              </TableCell>
              <TableCell className="text-muted-foreground">{formatDate(alert.created_at)}</TableCell>
              <TableCell>
                {(alert.status === "open" || alert.status === "reviewing") && (
                  <div className="flex gap-2">
                    <NoteAction
                      label="Résoudre"
                      action={resolveComplianceAlertAction.bind(null, alert.id)}
                    />
                    <NoteAction
                      label="Rejeter"
                      variant="outline"
                      action={dismissComplianceAlertAction.bind(null, alert.id)}
                    />
                  </div>
                )}
              </TableCell>
            </TableRow>
          ))}
          {alerts.length === 0 && (
            <TableRow>
              <TableCell colSpan={6} className="text-center text-muted-foreground">
                Aucune alerte
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
