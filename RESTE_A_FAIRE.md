# NasrCash — Ce qui reste à faire

Résumé de l'écart entre le cahier des charges complet et l'état actuel du dépôt
(`backend/`, `admin/`, `mobile/`). Voir `CAHIER_DES_CHARGES_NASRCASH.md` et
`NASRCASH_TECH_SPEC.md` pour la spécification complète.

## 1. Vérification de l'app mobile (priorité la plus haute)

L'app Kotlin/Jetpack Compose (`mobile/`) a été écrite entièrement mais **jamais
compilée** — cet environnement n'a pas de SDK Android, Gradle ni d'émulateur.
Il faut :

- Ouvrir le projet dans Android Studio et corriger les erreurs de build de
  premier essai (versions de dépendances, petits écarts d'API).
- Tester le parcours complet sur émulateur : inscription → OTP → KYC →
  carte → paiement → retrait.
- Ajouter des tests instrumentés/unitaires côté mobile (aucun n'existe).

## 2. Back-office admin incomplet

Seules les actions en lecture (+ KYC approuver/rejeter) sont dans `admin/`.
Manquent les écrans pour :

- Gérer les cartes (bloquer/débloquer depuis l'admin).
- Gérer les taux de change et les frais (un endpoint sandbox existe déjà
  côté backend — `POST /sandbox/fx/update-rate` — mais aucune page admin).
- Gérer les plafonds (aucun plafond n'existe encore, voir point 3).
- Gérer les rôles/permissions des comptes admin.
- Consulter le journal d'audit (`audit_logs`) — la table existe et est déjà
  alimentée par tout le backend, mais rien ne l'affiche.
- Export comptable.

## 3. Modules "frais" et "limites" simplifiés

- **Frais** : taux fixes (`TOPUP_FEE_PERCENT`, `PAYMENT_FEE_PERCENT`,
  `WITHDRAWAL_FEE_PERCENT`) définis en configuration, pas la table
  `fees_rules` configurable par pays / provider / niveau KYC décrite dans le
  cahier (section 14.8).
- **Limites** : aucun plafond n'est appliqué (recharge min/max, plafond
  journalier/mensuel, nombre de cartes, etc. — section 14.9). Un utilisateur
  peut aujourd'hui recharger ou retirer un montant illimité.

## 4. Conformité et risque

Aucune des fonctionnalités de la section 15.6 / 14.9 n'existe :

- Pas d'alertes AML, pas de détection de comportements suspects.
- Pas de scoring de risque par utilisateur.
- Pas de gel de compte automatique.
- Pas de rapport d'activité conformité.

## 5. Notifications push

Seules les notifications in-app (table `notifications`, `GET /notifications`)
existent. FCM/OneSignal n'est pas intégré — explicitement marqué optionnel
dans le cahier ("seulement si le temps le permet").

## 6. Observabilité et CI/CD

- Pas de Sentry, pas de Prometheus/Grafana (mentionnés dans la stack
  recommandée du cahier, section 11.2).
- Pas de pipeline CI (GitHub Actions) pour lancer automatiquement les 90
  tests backend à chaque push/PR.
- `admin/` et `mobile/` n'ont pas de Dockerfile — seul `backend/` a un
  `docker-compose.yml`.

## 7. Support client

Pas de module ticketing/réclamations (section 14 mentionne un canal support
WhatsApp ou in-app — rien n'est implémenté).

## 8. Hors-scope volontaire (attendu à ce stade, pas un manque de qualité)

Ces points sont normaux pour un MVP sandbox et relèvent des phases
ultérieures du cahier (section 24, Phase 3+) :

- Intégration réelle Orange Money / MTN MoMo / Moov Money (aujourd'hui :
  `MockPaymentProvider`).
- Intégration réelle d'un partenaire carte Visa/Mastercard (aujourd'hui :
  `MockCardProvider`, aucune donnée de carte réelle n'existe nulle part).
- Tout l'aspect juridique/réglementaire (agrément BCRG, capital social,
  contrats partenaires) — hors du champ du code.
- Expansion multi-pays au-delà de la Guinée — l'architecture le permet déjà
  (table `countries`, `currency_code` partout) mais seul GN/GNF est seedé.

## En chiffres

| Domaine | État |
|---|---|
| Backend | ✅ 90 tests passants, tous les blocs 1-12 + retrait |
| Admin Next.js | ✅ Vérifié en live, mais couverture fonctionnelle partielle |
| Mobile Kotlin | ⚠️ Écrit, jamais compilé/testé |
| Frais/Limites configurables | ❌ Simplifié (taux fixes, aucun plafond) |
| Conformité/Risque | ❌ Non commencé |
| Push notifications | ❌ Non fait (optionnel) |
| CI/CD, observabilité | ❌ Non fait |
| Intégrations réelles (providers) | ❌ Hors scope MVP sandbox |
