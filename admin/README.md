# NasrCash Admin

Next.js back-office for NasrCash — dashboard, users, KYC review, transactions.
See `../CAHIER_DES_CHARGES_NASRCASH.md` and `../NASRCASH_TECH_SPEC.md` for the
full product and technical specification.

## Stack

Next.js (App Router) · TypeScript · Tailwind CSS · TanStack Query · React Hook Form · Zod

## Local development

```bash
cp .env.example .env.local   # NASRCASH_API_URL points at the backend
npm install
npm run dev
```

The backend (`../backend`) must be running at `NASRCASH_API_URL` (default
`http://localhost:8000`) with the bootstrap admin seeded (see backend README).

## Architecture

- **Auth**: `POST /api/v1/admin/auth/login` issues a separate admin JWT (distinct
  token type from the mobile user's, so a leaked user token can never reach
  these pages). The token is stored in an `httpOnly` cookie — never exposed to
  browser JS — set by the `loginAction` Server Action in `src/lib/actions.ts`.
- **Route protection**: `src/proxy.ts` (Next.js 16 renamed `middleware` to
  `proxy`) redirects based on cookie presence for UX only. The real
  authorization boundary is the backend, which re-validates the JWT and role
  on every request — every Server Component fetch and Server Action calls it
  directly and redirects to `/login` on a 401.
- **Data fetching**: Server Components (`src/app/dashboard/**/page.tsx`) fetch
  directly from the backend via `src/lib/backend.ts#backendFetch`, per
  Next.js's own guidance to avoid routing Server Component data through local
  Route Handlers. TanStack Query is used client-side only for the
  auto-refreshing "recent transactions" widget on the dashboard, via a thin
  Route Handler (`/api/admin/transactions`) that forwards the httpOnly cookie
  to the backend — the browser never holds the JWT.
- **Mutations**: KYC approve/reject are Server Functions (`src/lib/actions.ts`)
  invoked directly from a Client Component (`src/components/kyc-actions.tsx`),
  revalidating the KYC page on success.
- **UI**: hand-rolled shadcn/ui-style primitives in `src/components/ui/` (no
  external registry dependency) built on `class-variance-authority` +
  `tailwind-merge`.
