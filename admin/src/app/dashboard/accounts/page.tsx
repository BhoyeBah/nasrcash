import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CreateAdminAccountForm } from "@/components/create-admin-account-form";
import { AdminAccountRow } from "@/components/admin-account-row";
import { backendFetch } from "@/lib/backend";
import { formatDate } from "@/lib/utils";
import type { AdminAccount } from "@/lib/types";

export default async function AccountsPage() {
  const accounts = await backendFetch<AdminAccount[]>("/api/v1/admin/accounts");

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Comptes admin</h1>
        <p className="text-sm text-muted-foreground">
          Gestion des comptes du back-office — réservé au super_admin
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-foreground">Créer un compte</CardTitle>
        </CardHeader>
        <CardContent>
          <CreateAdminAccountForm />
        </CardContent>
      </Card>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Email</TableHead>
            <TableHead>Rôle</TableHead>
            <TableHead>Statut</TableHead>
            <TableHead>Créé le</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {accounts.map((account) => (
            <TableRow key={account.id}>
              <TableCell className="font-medium">{account.email}</TableCell>
              <TableCell>{account.role}</TableCell>
              <TableCell>
                <Badge variant={account.is_active ? "success" : "outline"}>
                  {account.is_active ? "actif" : "désactivé"}
                </Badge>
              </TableCell>
              <TableCell className="text-muted-foreground">{formatDate(account.created_at)}</TableCell>
              <TableCell>
                <AdminAccountRow account={account} />
              </TableCell>
            </TableRow>
          ))}
          {accounts.length === 0 && (
            <TableRow>
              <TableCell colSpan={5} className="text-center text-muted-foreground">
                Aucun compte admin
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
