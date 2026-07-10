import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { StatusBadge } from "@/components/ui/badge";
import { ActionButton } from "@/components/action-button";
import { backendFetch } from "@/lib/backend";
import { blockCardAction, unblockCardAction } from "@/lib/actions";
import { formatDate } from "@/lib/utils";
import type { AdminCardListItem } from "@/lib/types";

export default async function CardsPage() {
  const cards = await backendFetch<AdminCardListItem[]>("/api/v1/admin/cards?limit=100");

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Cartes virtuelles</h1>
        <p className="text-sm text-muted-foreground">{cards.length} carte(s)</p>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Carte</TableHead>
            <TableHead>Utilisateur</TableHead>
            <TableHead>Devise</TableHead>
            <TableHead>Statut</TableHead>
            <TableHead>Créée le</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {cards.map((card) => (
            <TableRow key={card.id}>
              <TableCell className="font-medium">{card.masked_pan}</TableCell>
              <TableCell className="font-mono text-xs">{card.user_id}</TableCell>
              <TableCell>{card.displayed_currency}</TableCell>
              <TableCell>
                <StatusBadge status={card.status} />
              </TableCell>
              <TableCell className="text-muted-foreground">{formatDate(card.created_at)}</TableCell>
              <TableCell>
                {card.status === "blocked" ? (
                  <ActionButton
                    label="Débloquer"
                    action={unblockCardAction.bind(null, card.id)}
                  />
                ) : card.status !== "closed" ? (
                  <ActionButton
                    label="Bloquer"
                    variant="destructive"
                    action={blockCardAction.bind(null, card.id)}
                  />
                ) : (
                  <span className="text-xs text-muted-foreground">—</span>
                )}
              </TableCell>
            </TableRow>
          ))}
          {cards.length === 0 && (
            <TableRow>
              <TableCell colSpan={6} className="text-center text-muted-foreground">
                Aucune carte
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
