import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ActionButton } from "@/components/action-button";
import { CreateFeeRuleForm } from "@/components/create-fee-rule-form";
import { backendFetch } from "@/lib/backend";
import { deactivateFeeRuleAction } from "@/lib/actions";
import type { FeeRule } from "@/lib/types";

export default async function FeesPage() {
  const rules = await backendFetch<FeeRule[]>("/api/v1/admin/fees");

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Frais</h1>
        <p className="text-sm text-muted-foreground">
          Règles scopées par pays / provider / niveau KYC — la plus spécifique s&apos;applique
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-foreground">Ajouter une règle</CardTitle>
        </CardHeader>
        <CardContent>
          <CreateFeeRuleForm />
        </CardContent>
      </Card>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Type</TableHead>
            <TableHead>Pays</TableHead>
            <TableHead>Provider</TableHead>
            <TableHead>KYC</TableHead>
            <TableHead>Taux</TableHead>
            <TableHead>Montant fixe</TableHead>
            <TableHead>Statut</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rules.map((rule) => (
            <TableRow key={rule.id}>
              <TableCell className="font-medium">{rule.fee_type}</TableCell>
              <TableCell>{rule.country_code ?? "—"}</TableCell>
              <TableCell>{rule.provider_name ?? "—"}</TableCell>
              <TableCell>{rule.kyc_level ?? "—"}</TableCell>
              <TableCell>{rule.rate ?? "—"}</TableCell>
              <TableCell>{rule.fixed_amount}</TableCell>
              <TableCell>
                <Badge variant={rule.is_active ? "success" : "outline"}>
                  {rule.is_active ? "active" : "inactive"}
                </Badge>
              </TableCell>
              <TableCell>
                {rule.is_active && (
                  <ActionButton
                    label="Désactiver"
                    variant="outline"
                    action={deactivateFeeRuleAction.bind(null, rule.id)}
                  />
                )}
              </TableCell>
            </TableRow>
          ))}
          {rules.length === 0 && (
            <TableRow>
              <TableCell colSpan={8} className="text-center text-muted-foreground">
                Aucune règle de frais
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
