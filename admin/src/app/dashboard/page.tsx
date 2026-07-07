import { Card, CardContent, CardHeader, CardTitle, CardValue } from "@/components/ui/card";
import { RecentTransactionsWidget } from "@/components/recent-transactions-widget";
import { backendFetch } from "@/lib/backend";
import { formatAmount } from "@/lib/utils";
import type { DashboardStats } from "@/lib/types";

export default async function DashboardPage() {
  const stats = await backendFetch<DashboardStats>("/api/v1/admin/dashboard");

  const tiles = [
    { label: "Utilisateurs", value: stats.users_count.toLocaleString("fr-FR") },
    { label: "KYC en attente", value: stats.kyc_pending_count.toLocaleString("fr-FR") },
    { label: "Cartes émises", value: stats.cards_count.toLocaleString("fr-FR") },
    {
      label: "Volume rechargé",
      value: formatAmount(stats.successful_topups_volume, "GNF"),
    },
    {
      label: "Volume payé",
      value: formatAmount(stats.settled_payments_volume, "GNF"),
    },
    {
      label: "Paiements refusés",
      value: stats.declined_payments_count.toLocaleString("fr-FR"),
    },
    { label: "Revenus NasrCash", value: formatAmount(stats.revenue_total, "GNF") },
    {
      label: "Solde wallets (cache)",
      value: formatAmount(stats.total_wallet_cached_balance, "GNF"),
    },
  ];

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Tableau de bord</h1>
        <p className="text-sm text-muted-foreground">
          Vue d&apos;ensemble de l&apos;activité NasrCash (Guinée, sandbox)
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {tiles.map((tile) => (
          <Card key={tile.label}>
            <CardHeader>
              <CardTitle>{tile.label}</CardTitle>
              <CardValue>{tile.value}</CardValue>
            </CardHeader>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-foreground">Transactions récentes</CardTitle>
        </CardHeader>
        <CardContent>
          <RecentTransactionsWidget />
        </CardContent>
      </Card>
    </div>
  );
}
