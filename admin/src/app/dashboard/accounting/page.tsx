import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function AccountingPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Export comptable</h1>
        <p className="text-sm text-muted-foreground">
          Export CSV de toutes les écritures du ledger (double-entrée)
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-foreground">Télécharger</CardTitle>
        </CardHeader>
        <CardContent>
          <a
            href="/api/admin/accounting/export"
            className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground hover:opacity-90"
          >
            Télécharger le CSV (toutes les écritures)
          </a>
        </CardContent>
      </Card>
    </div>
  );
}
