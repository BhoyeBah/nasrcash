import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { StatusBadge } from "@/components/ui/badge";
import { KycActions } from "@/components/kyc-actions";
import { backendFetch } from "@/lib/backend";
import { formatDate } from "@/lib/utils";
import type { AdminKycPendingItem } from "@/lib/types";

export default async function KycPage() {
  const profiles = await backendFetch<AdminKycPendingItem[]>("/api/v1/admin/kyc/pending?limit=100");

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">KYC en attente</h1>
        <p className="text-sm text-muted-foreground">
          {profiles.length} dossier(s) soumis ou en cours de revue
        </p>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Utilisateur</TableHead>
            <TableHead>Niveau demandé</TableHead>
            <TableHead>Statut</TableHead>
            <TableHead>Soumis le</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {profiles.map((profile) => (
            <TableRow key={profile.id}>
              <TableCell className="font-mono text-xs">{profile.user_id}</TableCell>
              <TableCell>{profile.level_requested}</TableCell>
              <TableCell>
                <StatusBadge status={profile.status} />
              </TableCell>
              <TableCell className="text-muted-foreground">
                {profile.submitted_at ? formatDate(profile.submitted_at) : "—"}
              </TableCell>
              <TableCell>
                <KycActions profileId={profile.id} />
              </TableCell>
            </TableRow>
          ))}
          {profiles.length === 0 && (
            <TableRow>
              <TableCell colSpan={5} className="text-center text-muted-foreground">
                Aucun dossier KYC en attente
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
