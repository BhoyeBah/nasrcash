# CAHIER DES CHARGES COMPLET — NASRCASH

**Projet** : NasrCash
**Nature** : Solution fintech de wallet local et cartes virtuelles internationales
**Pays pilote** : Guinée
**Devise pilote** : GNF
**Vision** : Guinée d'abord, Afrique ensuite
**Version** : 1.0
**Objectif** : Construire une plateforme scalable permettant aux utilisateurs de recharger un wallet local, créer une carte virtuelle, la recharger en devise locale et payer à l'international avec conversion automatique au moment du paiement.

## 1. Résumé exécutif

NasrCash est une solution fintech destinée à résoudre un problème majeur en Guinée et en Afrique francophone : la difficulté d'accès aux cartes Visa/Mastercard permettant d'effectuer des paiements internationaux.

Aujourd'hui, de nombreux utilisateurs disposent d'argent via Orange Money, MTN Mobile Money, Moov Money, cash ou autres moyens locaux, mais ils ne peuvent pas facilement payer des services comme Facebook Ads, Google Ads, TikTok Ads, Netflix, Apple, Amazon, Alibaba, hébergement web, outils IA, formations en ligne ou logiciels SaaS.

NasrCash propose une solution simple :

```text
L'utilisateur recharge son wallet en GNF
        ↓
Il transfère une partie du solde vers sa carte virtuelle
        ↓
La carte affiche un solde en GNF
        ↓
Il paie à l'international en USD/EUR/autre devise
        ↓
NasrCash convertit automatiquement au moment du paiement
        ↓
Le solde carte est débité en GNF
```

La Guinée représente le premier marché pilote. Cependant, NasrCash doit être construit dès le départ comme une plateforme scalable, capable de s'étendre vers d'autres pays africains avec d'autres devises, moyens de paiement, partenaires cartes et règles réglementaires.

En Guinée, les cartes bancaires et les paiements mobiles font partie des moyens de paiement électroniques reconnus dans l'écosystème des paiements, et la BCRG présente les paiements mobiles comme un moyen fortement en croissance. La BCRG a aussi lancé le 15 janvier 2025 le Switch National Monétique et Digital, visant notamment à moderniser les paiements électroniques, renforcer l'inclusion financière et favoriser l'économie numérique.

## 2. Vision du projet

### 2.1 Vision courte

NasrCash permet aux Africains de payer à l'international avec leur argent local.

### 2.2 Vision long terme

NasrCash ambitionne de devenir une infrastructure fintech panafricaine qui connecte les moyens de paiement locaux africains aux paiements internationaux.

À terme, NasrCash ne doit pas être seulement une application de cartes virtuelles. Elle doit devenir :

- un wallet local multi-pays ;
- une plateforme de cartes virtuelles internationales ;
- une solution de paiement pour particuliers et entrepreneurs ;
- une solution de gestion de dépenses pour entreprises ;
- une API fintech B2B ;
- une infrastructure de card issuing pour startups africaines ;
- une passerelle entre Mobile Money africain et commerce mondial.

### 2.3 Ambition stratégique

NasrCash doit être pensé comme un passeport financier numérique permettant à l'utilisateur africain de participer à l'économie mondiale sans être bloqué par l'absence de carte bancaire internationale.

## 3. Problématique

### 3.1 Problème principal

En Guinée, l'accès aux cartes bancaires internationales est limité, coûteux ou peu accessible pour une grande partie de la population. Beaucoup d'utilisateurs ont de l'argent localement, mais ils ne peuvent pas facilement l'utiliser pour payer à l'international.

### 3.2 Conséquences

- dépendance à des intermédiaires informels ;
- frais élevés ;
- risque d'arnaque ;
- absence de transparence sur les taux ;
- difficulté pour lancer des campagnes publicitaires ;
- difficulté pour acheter des outils numériques ;
- blocage des freelances, agences, e-commerçants et étudiants ;
- exclusion des non-bancarisés du commerce international.

### 3.3 Opportunité

```text
Argent local
        ↓
Wallet NasrCash
        ↓
Carte virtuelle rechargeable en devise locale
        ↓
Paiements internationaux
```

## 4. Objectifs du projet

### 4.1 Objectif général

Créer une plateforme fintech scalable permettant à un utilisateur de recharger un wallet local, créer une carte virtuelle, l'alimenter en devise locale et effectuer des paiements internationaux avec conversion automatique.

### 4.2 Objectifs spécifiques

- Lancer un MVP en Guinée.
- Permettre la recharge du wallet en GNF.
- Permettre la recharge par Orange Money, MTN, Moov ou autres moyens locaux selon disponibilité.
- Permettre la création de cartes virtuelles.
- Afficher le solde wallet et le solde carte en GNF.
- Déclencher la conversion uniquement au moment du paiement international.
- Afficher clairement le montant marchand, le taux, les frais et le montant débité en GNF.
- Mettre en place un back-office de gestion, conformité et supervision.
- Intégrer un mode sandbox pour tester avant les API officielles.
- Préparer l'expansion multi-pays.
- Préparer une future offre B2B/API.

## 5. Positionnement de NasrCash

- **Positionnement initial** : NasrCash est une carte virtuelle internationale rechargeable en GNF depuis la Guinée.
- **Positionnement long terme** : NasrCash est une plateforme fintech africaine qui permet de payer à l'international avec les moyens de paiement locaux.
- **Promesse utilisateur** : "Rechargez en GNF. Payez partout dans le monde."

Slogans possibles :

- NasrCash — votre argent local, vos paiements mondiaux.
- NasrCash — payez Facebook, Google, Netflix et vos outils en ligne depuis la Guinée.
- NasrCash — la carte internationale pensée pour l'Afrique.
- NasrCash — rechargez en GNF, payez en USD, EUR ou partout ailleurs.
- NasrCash — l'Afrique connectée au commerce mondial.

## 6. Cibles utilisateurs

### 6.1 Particuliers

jeunes actifs, étudiants, créateurs de contenu, utilisateurs de Netflix/Apple/Amazon/AliExpress, personnes non bancarisées, personnes ayant besoin d'une carte virtuelle simple.

### 6.2 Entrepreneurs et freelances

freelances digitaux, développeurs, graphistes, community managers, agences marketing, e-commerçants, vendeurs Instagram/TikTok, propriétaires de boutiques Shopify/WooCommerce.

### 6.3 Entreprises

PME, agences de communication, startups, écoles privées, ONG, entreprises payant des outils en ligne, équipes ayant besoin de cartes de dépenses.

### 6.4 Segment B2B futur

plateformes fintech, marketplaces, applications de livraison, plateformes e-commerce, SaaS africains, entreprises souhaitant émettre des cartes virtuelles via API.

## 7. Principe financier central

### 7.1 Règle principale

Dans NasrCash, l'utilisateur doit gérer son argent en devise locale. Pour le lancement en Guinée :

```text
Wallet utilisateur : GNF
Carte utilisateur : GNF
Paiement marchand : USD, EUR ou autre devise
Conversion : automatique au moment du paiement
Débit utilisateur : GNF
```

### 7.2 Pourquoi cette logique est meilleure

Cette approche est plus adaptée au marché guinéen, car l'utilisateur comprend son argent en GNF. Il ne doit pas être obligé de convertir manuellement son solde en USD avant d'utiliser sa carte.

```text
Je recharge 500 000 GNF.
Je mets 300 000 GNF sur ma carte.
Je paie Netflix.
NasrCash calcule automatiquement le montant à débiter.
```

### 7.3 Différence entre réalité utilisateur et réalité technique

**Côté utilisateur** : wallet en GNF, carte en GNF, historique en GNF, frais en GNF, solde restant en GNF.

**Côté technique** : Le provider carte peut fonctionner en USD, EUR ou autre devise de règlement. NasrCash devra donc gérer une couche technique de conversion et de réconciliation entre :

```text
Solde carte utilisateur en GNF
        ↓
Autorisation internationale en devise marchand
        ↓
Conversion GNF vers devise de règlement
        ↓
Règlement provider
```

### 7.4 Modèle recommandé

Le modèle idéal est un système de type authorization control ou just-in-time funding, si le partenaire carte le permet :

1. Le marchand demande une autorisation de paiement.
2. Le provider carte transmet la demande à NasrCash ou applique les règles définies.
3. NasrCash calcule l'équivalent en GNF.
4. NasrCash vérifie le solde carte GNF.
5. NasrCash autorise ou refuse.
6. Le solde carte GNF est débité.
7. La transaction est enregistrée dans le ledger.

Si le provider ne permet pas le just-in-time funding, NasrCash devra utiliser un compte technique préfinancé en devise internationale, tout en continuant d'afficher le solde utilisateur en GNF.

## 8. Flux utilisateur principal

### 8.1 Recharge wallet

```text
1. L'utilisateur choisit "Recharger mon wallet".
2. Il choisit Orange Money, MTN, Moov ou autre moyen disponible.
3. Il saisit le montant en GNF.
4. NasrCash affiche les frais et le montant net.
5. L'utilisateur confirme.
6. Le provider confirme le paiement.
7. Le wallet NasrCash est crédité en GNF.
```

Exemple :

```text
Recharge : 500 000 GNF
Frais recharge : 10 000 GNF
Montant net wallet : 490 000 GNF
```

### 8.2 Recharge de la carte

```text
1. L'utilisateur ouvre sa carte virtuelle.
2. Il clique sur "Recharger la carte".
3. Il saisit le montant en GNF.
4. NasrCash vérifie le solde wallet.
5. Le wallet est débité.
6. Le solde carte est crédité en GNF.
```

Exemple :

```text
Solde wallet : 490 000 GNF
Recharge carte : 300 000 GNF
Nouveau solde wallet : 190 000 GNF
Solde carte : 300 000 GNF
```

### 8.3 Paiement international

```text
1. L'utilisateur paie sur un site international.
2. Le marchand demande un paiement en USD, EUR ou autre devise.
3. NasrCash reçoit ou simule la demande d'autorisation.
4. NasrCash récupère le taux applicable.
5. NasrCash calcule le montant équivalent en GNF.
6. NasrCash ajoute les frais.
7. NasrCash vérifie le solde carte en GNF.
8. Si le solde est suffisant, le paiement est accepté.
9. Si le solde est insuffisant, le paiement est refusé.
10. L'utilisateur reçoit une notification.
```

Exemple :

```text
Marchand : Netflix
Montant marchand : 10 USD
Taux : 1 USD = 9 000 GNF
Montant converti : 90 000 GNF
Frais NasrCash : 2 700 GNF
Total débité : 92 700 GNF
Solde carte avant : 300 000 GNF
Solde carte après : 207 300 GNF
```

## 9. Fonctionnalités MVP

### 9.1 Application mobile client

inscription utilisateur, vérification OTP, connexion, mot de passe, PIN, biométrie, profil utilisateur, KYC, wallet GNF, recharge wallet, carte virtuelle, recharge carte en GNF, paiement simulé en sandbox, historique wallet, historique carte, notifications, support WhatsApp ou in-app, paramètres de sécurité.

### 9.2 Back-office admin

dashboard général, gestion utilisateurs, gestion KYC, gestion wallets, gestion cartes, gestion recharges, gestion paiements simulés, gestion taux de change, gestion frais, gestion limites, gestion providers, gestion pays, gestion devises, gestion alertes risques, journal d'audit, export comptable.

### 9.3 Super admin plateforme

pays, devises, moyens de paiement, providers carte, providers Mobile Money, frais, taux, plafonds, règles KYC, règles AML, statuts, rôles, permissions.

## 10. Mode sandbox avant les API officielles

### 10.1 Objectif du sandbox

Avant de recevoir les API officielles Orange Money, MTN, Moov ou du partenaire carte, NasrCash doit intégrer un environnement sandbox permettant de tester tous les flux métier : le parcours utilisateur, le wallet, le ledger, les frais, la recharge carte, la conversion automatique, les paiements internationaux simulés, les remboursements, les erreurs, le back-office, les notifications, la conformité opérationnelle.

### 10.2 Providers sandbox à créer

```text
MockPaymentProvider
OrangeMoneySandboxAdapter
MTNMoMoSandboxAdapter
MoovMoneySandboxAdapter
MockCardProvider
MockFXProvider
MockKYCProvider
```

### 10.3 Principe technique

La logique métier ne doit pas dépendre directement d'un provider.

Mauvais modèle : `TopupService` appelle directement Orange Money.

Bon modèle : `TopupService` appelle `PaymentProviderAdapter`. L'adapter peut être sandbox ou production.

### 10.4 Flux recharge wallet sandbox

```text
1. L'utilisateur demande une recharge de 500 000 GNF.
2. NasrCash crée une topup_request.
3. Le MockPaymentProvider retourne un statut pending.
4. L'admin ou le simulateur confirme successful.
5. Le wallet est crédité.
6. Le ledger est mis à jour.
7. L'utilisateur reçoit une notification.
```

### 10.5 Flux carte sandbox

```text
1. L'utilisateur demande la création d'une carte.
2. NasrCash vérifie le KYC.
3. NasrCash vérifie les frais.
4. Le MockCardProvider génère une carte virtuelle test.
5. La carte apparaît dans l'application.
6. L'utilisateur peut la recharger en GNF.
```

### 10.6 Flux paiement sandbox

```text
1. L'utilisateur simule un paiement de 10 USD.
2. NasrCash récupère le taux USD/GNF.
3. NasrCash calcule le montant à débiter en GNF.
4. NasrCash ajoute les frais.
5. NasrCash vérifie le solde carte.
6. La transaction est acceptée ou refusée.
7. L'historique est mis à jour.
```

### 10.7 Endpoints sandbox

```text
POST /api/v1/sandbox/topups/{id}/simulate-success
POST /api/v1/sandbox/topups/{id}/simulate-failure
POST /api/v1/sandbox/cards/{id}/simulate-payment
POST /api/v1/sandbox/cards/{id}/simulate-refund
POST /api/v1/sandbox/cards/{id}/simulate-decline
POST /api/v1/sandbox/fx/update-rate
```

Ces endpoints doivent être désactivés en production.

## 11. Architecture technique recommandée

### 11.1 Principe

NasrCash doit commencer avec un modular monolith propre, puis évoluer vers des services séparés lorsque le volume augmente.

### 11.2 Stack backend recommandée

```text
FastAPI
PostgreSQL
SQLAlchemy 2.x
Alembic
Redis
Celery ou RQ
Pydantic
JWT
Docker
OpenAPI
Sentry
Prometheus / Grafana
```

### 11.3 Stack mobile recommandée

```text
Kotlin
Jetpack Compose
Room pour cache local non sensible
DataStore
Retrofit ou Ktor
Biometric API
Firebase ou OneSignal pour notifications
```

### 11.4 Stack admin recommandée

```text
Next.js
TypeScript
Tailwind CSS
shadcn/ui
TanStack Query
React Hook Form
Zod
```

### 11.5 Structure backend

```text
app/
├── modules/
│   ├── auth/
│   ├── users/
│   ├── kyc/
│   ├── wallets/
│   ├── cards/
│   ├── topups/
│   ├── payments/
│   ├── fx/
│   ├── ledger/
│   ├── fees/
│   ├── limits/
│   ├── countries/
│   ├── providers/
│   ├── compliance/
│   ├── risk/
│   ├── notifications/
│   ├── support/
│   └── admin/
└── core/
    ├── config.py
    ├── database.py
    ├── security.py
    ├── exceptions.py
    └── permissions.py
```

## 12. Architecture scalable multi-pays

### 12.1 Règle absolue

Aucun pays, aucune devise, aucun provider et aucun taux ne doit être codé en dur. La Guinée est le premier marché, mais le système doit pouvoir gérer demain : Sénégal, Côte d'Ivoire, Mali, Bénin, Togo, Burkina Faso, Cameroun, Gabon, RDC, autres pays.

### 12.2 Configuration par pays

code pays, devise locale, préfixe téléphonique, moyens de paiement disponibles, providers actifs, documents KYC acceptés, frais, plafonds, taux, règles AML, règles fiscales éventuelles, canaux support, langues, fuseau horaire.

### 12.3 Exemple

```text
Pays : Guinée
Code : GN
Devise : GNF
Moyens de recharge : Orange Money, MTN, Moov, cash agent
Carte : carte virtuelle internationale
Solde affiché : GNF
Conversion : au moment du paiement
```

Demain :

```text
Pays : Sénégal
Code : SN
Devise : XOF
Moyens de recharge : Wave, Orange Money, Free Money
Carte : carte virtuelle internationale
Solde affiché : XOF
Conversion : au moment du paiement
```

## 13. Ledger et comptabilité interne

### 13.1 Principe

NasrCash doit utiliser un ledger double-entry. Chaque opération financière doit être équilibrée : recharge wallet, frais recharge, recharge carte, frais carte, paiement international, frais de change, remboursement, annulation, ajustement manuel, commission provider, revenus NasrCash.

### 13.2 Exemple recharge wallet

```text
Transaction : TOPUP_SUCCESS

Débit  : Compte provider Orange Money     500 000 GNF
Crédit : Wallet utilisateur               500 000 GNF
```

### 13.3 Exemple recharge carte

```text
Transaction : CARD_TOPUP

Débit  : Wallet utilisateur GNF           300 000 GNF
Crédit : Solde carte utilisateur GNF      300 000 GNF
```

### 13.4 Exemple paiement international

```text
Transaction : CARD_PAYMENT_WITH_FX

Montant marchand : 10 USD
Taux : 1 USD = 9 000 GNF
Montant converti : 90 000 GNF
Frais : 2 700 GNF
Total débité : 92 700 GNF

Débit  : Solde carte utilisateur GNF      92 700 GNF
Crédit : Compte settlement provider       90 000 GNF
Crédit : Revenus NasrCash                 2 700 GNF
```

### 13.5 Exemple remboursement

```text
Transaction : CARD_REFUND

Débit  : Compte settlement provider       90 000 GNF
Crédit : Solde carte utilisateur GNF      90 000 GNF
```

Les frais peuvent être remboursés ou non selon la politique commerciale.

## 14. Modules fonctionnels détaillés

### 14.1 Module Authentification

Fonctionnalités : inscription, OTP, connexion, refresh token, PIN, biométrie, changement mot de passe, réinitialisation mot de passe, gestion des sessions, déconnexion de tous les appareils.

Sécurité : limitation des tentatives, verrouillage temporaire, détection appareil inconnu, notification de connexion, tokens expirables, rotation refresh token.

### 14.2 Module Utilisateur

Fonctionnalités : profil, téléphone, email, pays, adresse, profession, niveau KYC, statut compte, préférences de notifications.

Statuts utilisateur :

```text
active
pending_kyc
restricted
suspended
closed
```

### 14.3 Module KYC

Niveaux KYC :

```text
KYC 0 : compte créé, accès limité
KYC 1 : identité + téléphone + document + selfie
KYC 2 : justificatif adresse + source des fonds
KYC Business : documents entreprise + représentant légal
```

Statuts KYC :

```text
draft
submitted
under_review
approved
rejected
requires_more_info
expired
```

Documents possibles : carte nationale d'identité, passeport, permis si accepté, selfie, justificatif d'adresse, documents entreprise pour compte business.

### 14.4 Module Wallet

Fonctionnalités : création automatique du wallet à l'inscription, solde disponible, solde en attente, solde bloqué, historique, recharge, transfert wallet vers carte, remboursement carte vers wallet si autorisé, blocage administratif.

Types de soldes :

```text
available_balance
pending_balance
blocked_balance
```

### 14.5 Module Carte virtuelle

Fonctionnalités : demande création carte, création carte via provider sandbox ou live, affichage carte masquée, affichage sécurisé des détails, recharge carte en GNF, blocage, déblocage, fermeture, remplacement, historique, plafonds, notifications.

Statuts carte :

```text
requested
issuing
active
frozen
blocked
closed
expired
failed
```

### 14.6 Module Paiements internationaux

Fonctionnalités : réception/simulation demande paiement, calcul taux, calcul frais, vérification solde carte, autorisation, refus, débit en GNF, notification, historique.

Statuts paiement :

```text
authorized
declined
settled
reversed
refunded
chargeback
pending
```

Motifs de refus :

```text
insufficient_balance
card_frozen
card_blocked
kyc_required
limit_exceeded
risk_rejected
provider_error
unsupported_merchant
```

### 14.7 Module FX / Change

Fonctionnalités : taux USD/GNF, taux EUR/GNF, taux configurable, marge de change, taux par pays, taux par provider, historique des taux, taux figé par transaction.

Règles : le taux appliqué doit être historisé ; le taux doit être figé au moment de l'autorisation ; le reçu doit afficher le taux ; une transaction ne doit jamais être recalculée après coup.

### 14.8 Module Frais

Types de frais : frais recharge wallet, frais création carte, frais recharge carte, frais paiement international, marge FX, frais remplacement carte, frais abonnement premium, frais business, frais API B2B futur.

Les frais doivent être configurables par : pays, devise, provider, type utilisateur, niveau KYC, offre commerciale.

### 14.9 Module Limites

recharge minimale, recharge maximale, plafond journalier wallet, plafond mensuel wallet, plafond carte, plafond paiement journalier, plafond paiement mensuel, nombre de cartes, plafond par niveau KYC, plafond par pays, plafond par catégorie de marchand.

### 14.10 Module Notifications

Canaux : push mobile, SMS, email, WhatsApp plus tard, notification in-app.

Notifications : compte créé, OTP, KYC soumis, KYC approuvé, recharge reçue, carte créée, carte rechargée, paiement accepté, paiement refusé, carte bloquée, alerte sécurité.

## 15. Back-office admin

### 15.1 Dashboard

nombre d'utilisateurs, KYC en attente, volume recharge, volume cartes, volume paiements, revenus, alertes risques, transactions refusées, incidents providers, solde total wallet, solde total carte.

### 15.2 Gestion utilisateurs

rechercher un utilisateur, voir son profil, voir son statut, consulter son KYC, voir ses wallets, voir ses cartes, voir son historique, bloquer/débloquer, ajouter une note interne.

### 15.3 Gestion KYC

voir les KYC soumis, consulter les documents, approuver, rejeter, demander un complément, historiser la décision.

### 15.4 Gestion recharges

voir toutes les recharges, filtrer par statut, confirmer manuellement en sandbox, consulter les références provider, exporter, déclencher une revue manuelle.

### 15.5 Gestion cartes

voir les cartes créées, voir leur statut, bloquer une carte, consulter l'historique, voir les incidents provider, voir les paiements refusés.

### 15.6 Gestion conformité

alertes AML, détection multi-comptes, détection transactions inhabituelles, revue manuelle, gel compte, rapport d'activité, audit log.

## 16. Rôles et permissions

### 16.1 Rôles internes

```text
Super Admin
Admin Pays
Compliance Officer
Finance Manager
Risk Analyst
Support Agent
Operations Agent
Auditor
Developer Admin
```

### 16.2 Règles de sécurité

- Le support ne doit pas modifier les soldes.
- Un développeur ne doit pas valider un KYC en production.
- Un admin pays ne doit pas voir les autres pays sauf permission.
- Toute action sensible doit être journalisée.
- Les modifications de solde doivent nécessiter une justification.
- Les actions critiques doivent idéalement nécessiter une double validation.

## 17. Modèle réglementaire et juridique

### 17.1 Principe important

NasrCash ne doit pas démarrer en se présentant comme une banque. La solution touche aux moyens de paiement, au wallet, à la monnaie électronique, aux cartes et à la gestion de fonds clients. Elle doit donc être structurée légalement avec prudence.

### 17.2 Modèle recommandé au lancement

```text
NasrCash = application + expérience client + distribution + wallet technique + support + conformité opérationnelle
Partenaire agréé = émission réglementée / conservation des fonds / programme carte
Processor carte = infrastructure cartes virtuelles
Réseau carte = Visa ou Mastercard
```

### 17.3 Options réglementaires

**Option A — Agent ou distributeur d'un acteur agréé** : lancement plus rapide, risque réglementaire réduit, coûts plus faibles, mais dépendance au partenaire, marge plus faible, contrôle limité.

**Option B — Program Manager carte** : NasrCash gère la marque, l'application, la relation client et les opérations, tandis qu'un BIN sponsor ou une institution autorisée porte l'émission réglementée. Modèle fintech sérieux, scalable, adapté à une expansion multi-pays, mais contrats complexes, forte exigence conformité, dépendance au sponsor.

**Option C — Agrément propre** : NasrCash demande un agrément d'établissement de monnaie électronique ou autre statut adapté. Contrôle plus fort, meilleure valorisation, meilleure marge, mais capital important, délais, conformité lourde, reporting réglementaire.

En Guinée, une décision BCRG fixe le capital social minimum des établissements de monnaie électronique à 4 milliards GNF.

### 17.4 Recommandation

```text
Démarrer avec un partenaire agréé.
Tester en sandbox.
Signer les partenariats officiels.
Lancer un pilote fermé.
Évoluer progressivement vers un agrément propre si le volume le justifie.
```

### 17.5 Obligations à anticiper

KYC, AML, surveillance des transactions, plafonds, détection fraude, reporting, journal d'audit, gestion des réclamations, protection des données, sécurité des cartes, politique de conservation des données.

La BCRG dispose d'une instruction relative aux normes prudentielles applicables aux établissements de monnaie électronique, visant une gestion prudente de leurs activités.

## 18. Sécurité

### 18.1 Sécurité générale

HTTPS obligatoire, chiffrement des données sensibles, hashage sécurisé des mots de passe, MFA pour admin, PIN utilisateur, biométrie mobile, limitation des tentatives, rate limiting, audit log, sauvegardes chiffrées, monitoring, détection comportements suspects.

### 18.2 Sécurité carte

NasrCash doit réduire son exposition aux données carte. Règles : ne pas stocker le PAN complet ; ne pas stocker le CVV ; utiliser les tokens du provider ; masquer le numéro carte ; afficher les détails seulement après PIN ou biométrie ; limiter l'affichage dans le temps ; journaliser l'accès aux données sensibles ; privilégier les SDK/iframe du provider si disponible.

PCI DSS s'applique aux entités qui stockent, traitent ou transmettent des données titulaires de carte ou des données d'authentification sensibles, ainsi qu'aux entités pouvant impacter la sécurité de l'environnement de données carte. Le PCI Security Standards Council définit les données de compte comme incluant les données titulaires de carte et/ou les données d'authentification sensibles.

## 19. Modèle de données principal

### 19.1 Tables principales

```text
users, user_profiles, user_devices, user_sessions,
countries, currencies,
wallets, wallet_accounts,
cards, card_balances, card_transactions,
topups, payment_requests,
fx_rates, fx_quotes,
ledger_transactions, ledger_entries,
fees_rules, limits_rules,
kyc_profiles, kyc_documents, kyc_reviews,
providers, provider_events,
compliance_alerts, risk_scores,
notifications, support_tickets,
audit_logs,
admin_users, roles, permissions
```

### 19.2 Table wallets

```text
wallets
- id
- user_id
- country_code
- currency_code
- available_balance
- pending_balance
- blocked_balance
- status
- created_at
- updated_at
```

### 19.3 Table cards

```text
cards
- id
- user_id
- provider
- provider_card_id
- masked_pan
- last4
- brand
- displayed_currency
- technical_settlement_currency
- status
- nickname
- expiry_month
- expiry_year
- created_at
- updated_at
```

### 19.4 Table card_balances

```text
card_balances
- id
- card_id
- currency_code
- available_balance
- pending_balance
- blocked_balance
- updated_at
```

Pour la Guinée, `currency_code = GNF`.

### 19.5 Table card_transactions

```text
card_transactions
- id
- card_id
- merchant_name
- merchant_country
- merchant_currency
- merchant_amount
- fx_rate
- local_currency
- local_amount
- fees_amount
- total_debited
- status
- provider_reference
- created_at
```

### 19.6 Table ledger_entries

```text
ledger_entries
- id
- ledger_transaction_id
- account_id
- direction
- amount
- currency
- description
- created_at
```

## 20. API principales

### 20.1 Auth

```text
POST /api/v1/auth/register
POST /api/v1/auth/verify-otp
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
POST /api/v1/auth/forgot-password
POST /api/v1/auth/reset-password
POST /api/v1/auth/change-pin
```

### 20.2 Utilisateur

```text
GET /api/v1/me
PATCH /api/v1/me
GET /api/v1/me/devices
DELETE /api/v1/me/devices/{id}
```

### 20.3 KYC

```text
POST /api/v1/kyc/start
POST /api/v1/kyc/documents
POST /api/v1/kyc/submit
GET /api/v1/kyc/status
```

### 20.4 Wallet

```text
GET /api/v1/wallets
GET /api/v1/wallets/{id}/balance
GET /api/v1/wallets/{id}/transactions
POST /api/v1/wallets/{id}/topup
```

### 20.5 Carte

```text
POST /api/v1/cards
GET /api/v1/cards
GET /api/v1/cards/{id}
POST /api/v1/cards/{id}/fund
POST /api/v1/cards/{id}/freeze
POST /api/v1/cards/{id}/unfreeze
POST /api/v1/cards/{id}/close
GET /api/v1/cards/{id}/transactions
```

### 20.6 Paiement carte

```text
POST /api/v1/card-payments/authorize
POST /api/v1/card-payments/settle
POST /api/v1/card-payments/reverse
POST /api/v1/card-payments/refund
```

### 20.7 FX

```text
GET /api/v1/fx/rates
POST /api/v1/fx/quote
POST /api/v1/fx/admin/update-rate
```

### 20.8 Admin

```text
GET /api/v1/admin/dashboard
GET /api/v1/admin/users
GET /api/v1/admin/kyc/pending
POST /api/v1/admin/kyc/{id}/approve
POST /api/v1/admin/kyc/{id}/reject
GET /api/v1/admin/topups
GET /api/v1/admin/cards
GET /api/v1/admin/transactions
GET /api/v1/admin/reports
```

## 21. Interfaces providers

### 21.1 PaymentProvider

```python
class PaymentProvider:
    async def initiate_topup(self, amount, currency, phone, reference):
        raise NotImplementedError

    async def check_status(self, provider_reference):
        raise NotImplementedError

    async def handle_webhook(self, payload):
        raise NotImplementedError
```

### 21.2 CardProvider

```python
class CardProvider:
    async def create_card(self, user, currency):
        raise NotImplementedError

    async def freeze_card(self, card_reference):
        raise NotImplementedError

    async def unfreeze_card(self, card_reference):
        raise NotImplementedError

    async def close_card(self, card_reference):
        raise NotImplementedError

    async def get_transactions(self, card_reference):
        raise NotImplementedError
```

### 21.3 CardAuthorizationProvider

```python
class CardAuthorizationProvider:
    async def authorize_payment(
        self,
        card_id,
        merchant_amount,
        merchant_currency,
        merchant_name,
        provider_reference
    ):
        raise NotImplementedError
```

### 21.4 FXProvider

```python
class FXProvider:
    async def get_rate(self, from_currency, to_currency):
        raise NotImplementedError

    async def create_quote(self, from_currency, to_currency, amount):
        raise NotImplementedError
```

## 22. Expérience utilisateur mobile

### 22.1 Onboarding

Message principal : "Rechargez en GNF. Payez partout dans le monde."

Actions : créer un compte, se connecter, découvrir NasrCash.

### 22.2 Accueil

solde wallet GNF, solde carte GNF, bouton recharger, bouton créer carte, bouton recharger carte, dernières transactions, statut KYC.

### 22.3 Écran wallet

solde disponible, solde en attente, historique, bouton recharger, bouton transférer vers carte.

### 22.4 Écran carte

carte virtuelle, solde en GNF, numéro masqué, bouton afficher détails, bouton recharger carte, bouton bloquer, bouton débloquer, bouton supprimer, historique des paiements.

### 22.5 Notification paiement

```text
Paiement accepté ✅

Marchand : Netflix
Montant : 10 USD
Taux : 1 USD = 9 000 GNF
Frais : 2 700 GNF
Total débité : 92 700 GNF
Solde carte restant : 207 300 GNF
```

### 22.6 Paiement refusé

```text
Paiement refusé ❌

Marchand : Google Ads
Montant : 25 USD
Total requis : 231 750 GNF
Solde carte : 150 000 GNF

Motif : solde insuffisant.
```

## 23. Business model

### 23.1 Revenus B2C

frais de création carte, frais recharge wallet, frais recharge carte, marge sur taux de change, frais paiement international, frais remplacement carte, abonnement premium, frais de support prioritaire.

### 23.2 Revenus B2B

comptes entreprise, cartes pour employés, cartes publicitaires, cartes à usage unique, dashboard entreprise, API card issuing, frais par carte, frais par transaction, abonnement mensuel.

### 23.3 Offres possibles

- **Offre Standard** : 1 carte virtuelle, plafonds faibles, frais standards.
- **Offre Premium** : plusieurs cartes, plafonds plus élevés, frais réduits, support prioritaire.
- **Offre Business** : cartes multiples, sous-comptes, gestion dépenses, exports, limites par employé.
- **Offre API** : émission carte via API, webhooks, reporting, tarification par volume.

## 24. Roadmap

- **Phase 0 — Pré-cadrage** (2-4 semaines) : étude marché, landing page, liste d'attente, maquettes initiales, dossier partenaire, validation juridique préliminaire.
- **Phase 1 — Prototype UX/UI** (4-6 semaines) : maquette mobile, maquette admin, parcours wallet/carte/paiement international/KYC.
- **Phase 2 — MVP sandbox** (8-12 semaines) : backend, app mobile, back-office, wallet GNF, carte GNF sandbox, recharge wallet/carte sandbox, simulation paiement USD/EUR, conversion automatique, ledger, notifications, audit log.
- **Phase 3 — Intégration partenaires** (6-12 semaines) : intégration Mobile Money réelle, intégration provider carte, webhooks, rapprochement, sécurité, conformité, tests end-to-end.
- **Phase 4 — Pilote fermé Guinée** (8-12 semaines) : 100 à 500 utilisateurs vérifiés, tester les paiements réels, mesurer les incidents, corriger l'UX, valider le modèle économique.
- **Phase 5 — Lancement public Guinée** : lancement officiel, support structuré, marketing, partenariats agences, reporting opérationnel.
- **Phase 6 — Expansion multi-pays** : Sénégal, Côte d'Ivoire, Mali, Bénin, Togo, autres marchés.

## 25. Critères d'acceptation MVP

Le MVP sera accepté si :

- l'utilisateur peut créer un compte ;
- l'OTP fonctionne ;
- le KYC peut être soumis ;
- l'admin peut valider/rejeter le KYC ;
- l'utilisateur peut recharger son wallet en sandbox ;
- le wallet est crédité en GNF ;
- l'utilisateur peut créer une carte virtuelle sandbox ;
- l'utilisateur peut recharger la carte en GNF ;
- l'utilisateur peut simuler un paiement USD/EUR ;
- la conversion automatique fonctionne ;
- le solde carte est débité en GNF ;
- les frais sont calculés correctement ;
- le taux appliqué est historisé ;
- le ledger reste équilibré ;
- les transactions sont visibles côté utilisateur ;
- les transactions sont visibles côté admin ;
- les webhooks sandbox sont idempotents ;
- les données sensibles carte ne sont pas stockées en clair ;
- les logs d'audit existent.

## 26. Risques principaux

- **Risque réglementaire** : travailler avec un partenaire agréé, obtenir un avis juridique, ne pas se présenter comme banque, documenter les responsabilités, respecter les règles KYC/AML.
- **Risque provider carte** : architecture provider-agnostic, plusieurs providers possibles, sandbox interne, fallback technique, négociation claire sur settlement et autorisation.
- **Risque change** : taux dynamique, marge de sécurité, taux figé par transaction, suivi quotidien, réconciliation.
- **Risque fraude** : KYC fort, limites, scoring risque, surveillance transactions, blocage automatique, revue manuelle.
- **Risque liquidité** : ségrégation des fonds, compte de cantonnement avec partenaire, réconciliation quotidienne, interdiction d'utiliser les fonds clients pour les dépenses internes.

## 27. Indicateurs clés

- **Produit** : inscriptions, KYC soumis/validés, cartes créées/actives, recharges wallet/carte, paiements acceptés/refusés, temps moyen de traitement.
- **Business** : volume rechargé/payé, revenus frais, marge FX, revenu moyen par utilisateur, coût provider/KYC/support, rétention.
- **Risque** : alertes AML, comptes bloqués, transactions suspectes, chargebacks, paiements refusés, incidents provider.

## 28. Équipe nécessaire

- **Phase MVP** : chef de projet, expert fintech/conformité, backend developer, mobile developer, frontend admin developer, UI/UX designer, DevOps, QA/testeur, juriste fintech externe.
- **Phase croissance** : compliance officer, risk analyst, finance/reconciliation officer, support client, business developer, partnership manager, security engineer, data analyst.

## 29. Conclusion

NasrCash doit être construit comme une fintech sérieuse, scalable et conforme. La logique finale est :

```text
Wallet utilisateur : GNF
Carte utilisateur : GNF
Paiement international : USD/EUR/autre devise
Conversion : automatique au moment du paiement
Débit utilisateur : GNF
```

Cette approche simplifie fortement l'expérience utilisateur, car le client raisonne uniquement dans sa devise locale. Elle permet aussi à NasrCash de maîtriser le taux, les frais, les limites, le risque et la marge de change.

La stratégie recommandée est :

1. construire le MVP en sandbox ;
2. tester tout le parcours wallet → carte → paiement ;
3. préparer les partenariats réglementaires ;
4. intégrer les API officielles ;
5. lancer un pilote fermé en Guinée ;
6. lancer publiquement ;
7. étendre progressivement vers d'autres pays africains.

**Vision finale** : NasrCash doit devenir l'infrastructure qui permet aux Africains de transformer leur argent local en pouvoir de paiement mondial.
