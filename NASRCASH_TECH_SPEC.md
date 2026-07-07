# NasrCash — Spec technique de démarrage (backend sandbox MVP)

Ce document complète `CAHIER_DES_CHARGES_NASRCASH.md` (règles métier, flux, modèle de données de référence, critères d'acceptation) avec les contraintes techniques de mise en œuvre.

## Contexte

NasrCash MVP pour la Guinée, en mode sandbox (sans intégration réelle avec un partenaire pour l'instant) : wallet en GNF, recharge (dépôt), retrait, et carte Visa virtuelle rechargeable pour payer à l'international.

## Stack imposée

- **Backend** : FastAPI (Python 3.12), SQLAlchemy 2.x async, PostgreSQL, Alembic, Redis
- **Mobile** : Kotlin + Jetpack Compose, architecture MVVM + SOLID
- **Admin/back-office** : Next.js (TypeScript), Tailwind CSS

## Principes d'architecture non négociables

1. **Sandbox-first.** Aucune intégration réelle avec Orange Money, MTN, ou un provider de carte pour l'instant. Tout provider externe est un adapter derrière une interface abstraite (`PaymentProvider`, `CardProvider`, `FXProvider`), avec une implémentation `Mock*` par défaut. Le code métier ne doit jamais importer un SDK de provider directement.
2. **Ledger double-entrée append-only.** Aucun solde n'est jamais modifié directement (`UPDATE balance = ...` est interdit). Toute opération monétaire passe par un `LedgerService` qui écrit des `LedgerEntry` (débit + crédit équilibrés) rattachées à une `LedgerTransaction`. Le champ `balance` sur `wallets`/`card_balances` est une projection en cache, jamais la source de vérité.
3. **Idempotence obligatoire.** Chaque opération monétaire a une clé d'idempotence (`reference`). Rejouer la même requête ne doit jamais créer une deuxième écriture.
4. **Aucune donnée de carte sensible en clair.** PAN/CVV toujours masqués ou tokenisés, même en sandbox.
5. **Modular monolith.** Un seul service backend, organisé en modules indépendants (`app/modules/<nom>/{router,service,models,schemas}.py`), pas de microservices à ce stade.
6. **Rien en dur.** Pays, devise, provider, taux et frais doivent être configurables en base, jamais codés en dur dans la logique métier.
7. **Journal d'audit systématique.** Toute action sensible écrit une entrée dans `audit_logs`, table immuable (pas d'UPDATE ni DELETE applicatif dessus).

## Structure de dossiers backend

```
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── exceptions.py
│   │   └── permissions.py
│   └── modules/
│       ├── auth/
│       ├── users/
│       ├── kyc/
│       ├── wallets/
│       ├── ledger/
│       ├── topups/
│       ├── cards/
│       ├── payments/
│       ├── fx/
│       ├── fees/
│       ├── limits/
│       ├── providers/
│       ├── notifications/
│       ├── sandbox/
│       └── admin/
├── alembic/
├── tests/
├── docker-compose.yml
├── requirements.txt / pyproject.toml
└── .env.example
```

## Ordre de développement (blocs)

1. Setup — squelette FastAPI + docker-compose (Postgres, Redis) + Alembic + `/health`.
2. Auth — inscription téléphone, OTP simulé, login PIN, JWT access+refresh, verrouillage.
3. KYC — upload documents, niveaux 0/1/2, auto-approbation simulée.
4. Ledger + Wallets — `LedgerService` d'abord, puis wallets dessus.
5. Topups — `MockPaymentProvider`, flux pending → confirmation sandbox → crédit ledger.
6. Cartes virtuelles — `MockCardProvider`, émission (bloquée si KYC < 2), freeze/unfreeze, recharge.
7. Paiement international simulé — `MockFXProvider`, authorize → débit carte / crédit settlement / crédit revenus, taux figé.
8. Notifications — in-app minimum.
9. Backoffice (lecture) — dashboard, users, KYC pending, transactions.
10. App mobile Kotlin.
11. Admin Next.js.
12. Durcissement — audit, rate limiting, tests d'idempotence.

Statut d'avancement suivi dans les commits de ce dépôt.
