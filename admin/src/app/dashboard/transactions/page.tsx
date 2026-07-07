import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { backendFetch } from "@/lib/backend";
import { formatAmount, formatDate } from "@/lib/utils";
import type { AdminTransactionItem } from "@/lib/types";

export default async function TransactionsPage() {
  const transactions = await backendFetch<AdminTransactionItem[]>(
    "/api/v1/admin/transactions?limit=100",
  );

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Transactions</h1>
        <p className="text-sm text-muted-foreground">
          Écritures du ledger (double-entrée) — les 100 plus récentes
        </p>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Compte</TableHead>
            <TableHead>Sens</TableHead>
            <TableHead>Montant</TableHead>
            <TableHead>Devise</TableHead>
            <TableHead>Date</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {transactions.map((tx) => (
            <TableRow key={tx.id}>
              <TableCell className="font-mono text-xs">{tx.account_id}</TableCell>
              <TableCell>
                <Badge variant={tx.direction === "credit" ? "success" : "outline"}>
                  {tx.direction}
                </Badge>
              </TableCell>
              <TableCell>{formatAmount(tx.amount, tx.currency)}</TableCell>
              <TableCell>{tx.currency}</TableCell>
              <TableCell className="text-muted-foreground">
                {formatDate(tx.created_at)}
              </TableCell>
            </TableRow>
          ))}
          {transactions.length === 0 && (
            <TableRow>
              <TableCell colSpan={5} className="text-center text-muted-foreground">
                Aucune transaction
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
