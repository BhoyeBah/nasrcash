import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CreateFxRateForm } from "@/components/create-fx-rate-form";
import { backendFetch } from "@/lib/backend";
import { formatDate } from "@/lib/utils";
import type { FxRate } from "@/lib/types";

export default async function FxPage() {
  const rates = await backendFetch<FxRate[]>("/api/v1/admin/fx-rates");

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Taux de change</h1>
        <p className="text-sm text-muted-foreground">
          Historique append-only — chaque nouveau taux devient le taux actif pour la paire
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-foreground">Ajouter un taux</CardTitle>
        </CardHeader>
        <CardContent>
          <CreateFxRateForm />
        </CardContent>
      </Card>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Paire</TableHead>
            <TableHead>Taux</TableHead>
            <TableHead>Défini le</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rates.map((rate, index) => (
            <TableRow key={`${rate.base_currency}-${rate.quote_currency}-${index}`}>
              <TableCell className="font-medium">
                {rate.base_currency}/{rate.quote_currency}
              </TableCell>
              <TableCell>{rate.rate}</TableCell>
              <TableCell className="text-muted-foreground">{formatDate(rate.created_at)}</TableCell>
            </TableRow>
          ))}
          {rates.length === 0 && (
            <TableRow>
              <TableCell colSpan={3} className="text-center text-muted-foreground">
                Aucun taux configuré
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
