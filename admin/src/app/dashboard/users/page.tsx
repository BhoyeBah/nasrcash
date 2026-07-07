import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { StatusBadge } from "@/components/ui/badge";
import { backendFetch } from "@/lib/backend";
import { formatDate } from "@/lib/utils";
import type { AdminUserListItem } from "@/lib/types";

export default async function UsersPage() {
  const users = await backendFetch<AdminUserListItem[]>("/api/v1/admin/users?limit=100");

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Utilisateurs</h1>
        <p className="text-sm text-muted-foreground">{users.length} compte(s)</p>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Téléphone</TableHead>
            <TableHead>Pays</TableHead>
            <TableHead>Statut</TableHead>
            <TableHead>Niveau KYC</TableHead>
            <TableHead>Créé le</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {users.map((user) => (
            <TableRow key={user.id}>
              <TableCell className="font-medium">{user.phone}</TableCell>
              <TableCell>{user.country_code}</TableCell>
              <TableCell>
                <StatusBadge status={user.status} />
              </TableCell>
              <TableCell>{user.kyc_level}</TableCell>
              <TableCell className="text-muted-foreground">
                {formatDate(user.created_at)}
              </TableCell>
            </TableRow>
          ))}
          {users.length === 0 && (
            <TableRow>
              <TableCell colSpan={5} className="text-center text-muted-foreground">
                Aucun utilisateur
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
