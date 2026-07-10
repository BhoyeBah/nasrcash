import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ActionButton } from "@/components/action-button";
import { CreateLimitRuleForm } from "@/components/create-limit-rule-form";
import { backendFetch } from "@/lib/backend";
import { deactivateLimitRuleAction } from "@/lib/actions";
import { formatDate } from "@/lib/utils";
import type { LimitRule } from "@/lib/types";

export default async function LimitsPage() {
  const rules = await backendFetch<LimitRule[]>("/api/v1/admin/limits");

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Plafonds</h1>
        <p className="text-sm text-muted-foreground">
          Règles scopées par pays / niveau KYC — la règle la plus spécifique s&apos;applique
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-foreground">Ajouter une règle</CardTitle>
        </CardHeader>
        <CardContent>
          <CreateLimitRuleForm />
        </CardContent>
      </Card>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Type</TableHead>
            <TableHead>Pays</TableHead>
            <TableHead>KYC</TableHead>
            <TableHead>Montant max</TableHead>
            <TableHead>Nombre max</TableHead>
            <TableHead>Statut</TableHead>
            <TableHead>Créée le</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rules.map((rule) => (
            <TableRow key={rule.id}>
              <TableCell className="font-medium">{rule.limit_type}</TableCell>
              <TableCell>{rule.country_code ?? "—"}</TableCell>
              <TableCell>{rule.kyc_level ?? "—"}</TableCell>
              <TableCell>{rule.max_amount ?? "—"}</TableCell>
              <TableCell>{rule.max_count ?? "—"}</TableCell>
              <TableCell>
                <Badge variant={rule.is_active ? "success" : "outline"}>
                  {rule.is_active ? "active" : "inactive"}
                </Badge>
              </TableCell>
              <TableCell className="text-muted-foreground">{formatDate(rule.created_at)}</TableCell>
              <TableCell>
                {rule.is_active && (
                  <ActionButton
                    label="Désactiver"
                    variant="outline"
                    action={deactivateLimitRuleAction.bind(null, rule.id)}
                  />
                )}
              </TableCell>
            </TableRow>
          ))}
          {rules.length === 0 && (
            <TableRow>
              <TableCell colSpan={8} className="text-center text-muted-foreground">
                Aucune règle de plafond
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
