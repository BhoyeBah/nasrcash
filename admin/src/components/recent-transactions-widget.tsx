"use client";

import { useQuery } from "@tanstack/react-query";

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { formatAmount, formatDate } from "@/lib/utils";
import type { AdminTransactionItem } from "@/lib/types";

async function fetchRecentTransactions(): Promise<AdminTransactionItem[]> {
  const response = await fetch("/api/admin/transactions");
  if (!response.ok) throw new Error("Impossible de charger les transactions");
  return response.json();
}

export function RecentTransactionsWidget() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["recent-transactions"],
    queryFn: fetchRecentTransactions,
    refetchInterval: 10_000,
  });

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Chargement...</p>;
  }

  if (error) {
    return <p className="text-sm text-destructive">Impossible de charger les transactions.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Compte</TableHead>
          <TableHead>Sens</TableHead>
          <TableHead>Montant</TableHead>
          <TableHead>Date</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {data?.map((tx) => (
          <TableRow key={tx.id}>
            <TableCell className="font-mono text-xs">{tx.account_id}</TableCell>
            <TableCell>
              <Badge variant={tx.direction === "credit" ? "success" : "outline"}>
                {tx.direction}
              </Badge>
            </TableCell>
            <TableCell>{formatAmount(tx.amount, tx.currency)}</TableCell>
            <TableCell className="text-muted-foreground">{formatDate(tx.created_at)}</TableCell>
          </TableRow>
        ))}
        {data?.length === 0 && (
          <TableRow>
            <TableCell colSpan={4} className="text-center text-muted-foreground">
              Aucune transaction pour le moment
            </TableCell>
          </TableRow>
        )}
      </TableBody>
    </Table>
  );
}
