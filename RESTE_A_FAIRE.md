# NasrCash — Ce qui reste à faire

Résumé de l'écart entre le cahier des charges complet et l'état actuel du dépôt
(`backend/`, `admin/`, `mobile/`). Voir `CAHIER_DES_CHARGES_NASRCASH.md` et
`NASRCASH_TECH_SPEC.md` pour la spécification complète.

## 1. Vérification de l'app mobile

En revoyant l'app côté fonctionnalités, un vrai trou a été trouvé et corrigé :
il n'existait aucun écran pour **créer une carte virtuelle** (`issueCard()`
existait déjà dans le repository/API client mais rien ne l'appelait) — un
utilisateur KYC2 n'avait aucun moyen d'en créer une depuis l'app. Corrigé sur
`HomeScreen`/`HomeViewModel`. Un module **support client** (créer un ticket,
lister ses tickets, fil de discussion + réponse) a aussi été ajouté.

L'app Kotlin/Jetpack Compose (`mobile/`) reste cependant **jamais compilée**
— cet environnement n'a pas de SDK Android ni d'émulateur (Gradle est présent
mais `ANDROID_HOME` ne l'est pas). Il faut :

- Ouvrir le projet dans Android Studio et corriger les erreurs de build de
  premier essai (versions de dépendances, petits écarts d'API).
- Tester le parcours complet sur émulateur : inscription → OTP → KYC →
  carte → paiement → retrait → support.
- Ajouter des tests instrumentés/unitaires côté mobile (aucun n'existe).

## 2. Back-office admin — ✅ fait

Écrans ajoutés dans `admin/` (en plus des écrans lecture + KYC déjà en place) :
cartes (bloquer/débloquer), taux de change (historique + création — remplace
l'endpoint sandbox-only), plafonds et frais (CRUD), conformité/risque (alertes,
score de risque, débloquer un compte, export CSV), support client (liste +
fil de discussion), journal d'audit (filtrable), export comptable CSV, et
gestion des comptes admin (créer/changer de rôle/désactiver — super_admin
uniquement). Vérifié en direct dans un vrai navigateur contre le backend
(voir historique de commit) : blocage/déblocage de carte, création de taux
FX, désactivation de règle, réponse à un ticket, création de compte admin,
et résolution d'alerte avec consultation du score de risque fonctionnent
de bout en bout.

## 3. Modules "frais" et "limites" — ✅ fait

- **Frais** : table `fee_rules` configurable par pays / provider / niveau KYC
  (section 14.8), avec endpoints admin CRUD (`/admin/fees`). Les anciens taux
  fixes (`TOPUP_FEE_PERCENT`, etc.) ont été supprimés de la config.
- **Limites** : table `limit_rules` configurable par pays / niveau KYC
  (section 14.9) — recharge min/max, plafond glissant 24h (recharge, retrait,
  paiement carte), nombre max de cartes. Endpoints admin CRUD (`/admin/limits`).
  Un dépassement décline le paiement carte ou rejette la recharge/retrait/
  émission de carte avec `422 limit_exceeded`.

## 4. Conformité et risque — ✅ fait

Implémenté (`app/modules/compliance/`) :

- Alertes automatiques : transaction importante (`large_transaction`, seuil
  configurable, sévérité jusqu'à `critical` au-delà de 10x le seuil),
  vélocité (`velocity`), tentative de dépassement de plafond
  (`limit_exceeded_attempt`).
- Score de risque agrégé par utilisateur (somme pondérée des alertes
  ouvertes sur une fenêtre glissante) et **gel de compte automatique**
  (compte suspendu + wallet bloqué) quand le score dépasse un seuil
  configurable — un compte gelé est rejeté partout via `get_current_user`,
  et un paiement carte décline avec `account_frozen`.
  Déblocage manuel par un admin conformité.
- Rapport d'activité conformité exportable en CSV.
- Endpoints admin : lister/résoudre/rejeter une alerte, score de risque,
  débloquer un compte, export — gated aux rôles compliance/risk/audit.

## 5. Support client — ✅ fait (canal in-app uniquement)

Nouveau module (`app/modules/support/`) : un utilisateur crée un ticket et y
répond ; un admin liste/répond/résout/ferme les tickets, avec notification
in-app au client à chaque réponse admin. Écrans admin et mobile ajoutés.
Le canal WhatsApp mentionné au cahier (§14) n'est pas fait — nécessite une
clé API WhatsApp Business que nous n'avons pas dans ce sandbox.

## 6. CI/CD — ✅ fait (backend uniquement)

Pipeline GitHub Actions (`.github/workflows/backend-tests.yml`) qui lance les
134 tests backend (Postgres + Redis en services) sur chaque push/PR touchant
`backend/`.

Reste non fait :
- Pas de Sentry, pas de Prometheus/Grafana (mentionnés dans la stack
  recommandée du cahier, section 11.2) — nécessitent un compte/clé externe.
- Pas de pipeline CI pour `admin/` (build/lint) ni `mobile/` (pas de SDK
  Android disponible pour un runner de toute façon).
- `admin/` et `mobile/` n'ont pas de Dockerfile — seul `backend/` a un
  `docker-compose.yml`.

## 7. Notifications push

Seules les notifications in-app (table `notifications`, `GET /notifications`)
existent. FCM/OneSignal n'est pas intégré — explicitement marqué optionnel
dans le cahier ("seulement si le temps le permet"), et nécessite un projet
Firebase que nous n'avons pas.

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
| Backend | ✅ 134 tests passants — tous les blocs + retrait + frais/limites + conformité + support |
| Admin Next.js | ✅ Toutes les fonctionnalités backend ont un écran, vérifié en direct |
| Mobile Kotlin | ⚠️ Écrit (dont support client), jamais compilé/testé — pas de SDK Android ici |
| Frais/Limites configurables | ✅ Fait |
| Conformité/Risque | ✅ Fait (alertes, score, gel auto + déblocage, export) |
| Support client | ✅ Fait (in-app) — WhatsApp non fait (clé API manquante) |
| CI/CD backend | ✅ Fait (GitHub Actions) |
| Observabilité (Sentry/Prometheus) | ❌ Non fait (nécessite des clés externes) |
| Push notifications | ❌ Non fait (optionnel, nécessite un projet Firebase) |
| Intégrations réelles (providers) | ❌ Hors scope MVP sandbox |
