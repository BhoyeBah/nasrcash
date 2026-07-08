# NasrCash Mobile (Android)

Kotlin + Jetpack Compose client for the NasrCash sandbox MVP — onboarding/OTP,
PIN + biometric unlock, wallet overview, deposits, KYC document upload,
virtual card management, transaction history, and notifications. See
`../CAHIER_DES_CHARGES_NASRCASH.md` and `../NASRCASH_TECH_SPEC.md` for the
full product and technical specification.

## ⚠️ Build status

This module was written in an environment **without an Android SDK, Gradle,
or an emulator available** — unlike `backend/` (79 passing pytest tests) and
`admin/` (built, linted, and verified end-to-end against the live backend
with screenshots), **this code has not been compiled or run**. Open it in
Android Studio and expect to fix the usual first-build issues (dependency
version bumps, minor API mismatches) before it runs. The architecture and
API contracts are deliberately kept simple and closely mirror the backend's
actual schemas to minimize that risk, but treat this as a solid first draft
to build from, not a verified deliverable.

## Stack

Kotlin · Jetpack Compose · Material 3 · Navigation Compose · Retrofit +
kotlinx.serialization · Room (local cache) · EncryptedSharedPreferences ·
androidx.biometric

## Running against the backend

The emulator reaches the host machine's `localhost` via `10.0.2.2` — see
`API_BASE_URL` in `app/build.gradle.kts`. Start the backend first:

```bash
cd ../backend
docker compose up -d postgres redis
alembic upgrade head
uvicorn app.main:app --reload
```

Then open `mobile/` in Android Studio and run on an emulator or device.

## Architecture (MVVM + repository pattern)

```
ui/<feature>/FooScreen.kt        Compose UI only — no network/session code
ui/<feature>/FooViewModel.kt     Holds UiState, calls repositories, never Retrofit directly
data/repository/FooRepository.kt Wraps ApiService calls in ApiResult<T>, the only network boundary
core/network/                    ApiService (Retrofit interface), DTOs, auth interceptor + refresh
core/session/TokenStore.kt       Access/refresh tokens in EncryptedSharedPreferences (Keystore-backed)
core/session/BiometricHelper.kt  BiometricPrompt wrapper for app-relock on cold start
core/di/AppContainer.kt          Manual DI — one file wires every dependency, no Hilt/Koin
data/local/                      Room cache for notifications only (explicitly non-sensitive data)
```

Key rules carried over from the backend's discipline:

- **ViewModels never import Retrofit or OkHttp** — only repositories, which
  return a `ApiResult<T>` (`Success`/`Error`) so no ViewModel needs a
  try/catch around a network call.
- **No PAN/CVV ever appears client-side.** The backend's `CardResponse` only
  ever contains a masked PAN — there is nothing to redact in the app because
  there is nothing sensitive to receive in the first place.
- **Money-moving calls are idempotent.** `CardRepository.fund()` generates a
  fresh idempotency key per user tap, matching the backend's
  `idempotency_key` contract on `POST /cards/{id}/fund`.
- **Sandbox is explicit in the UI**, not hidden: the topup screen shows a
  distinct "pending → confirm (sandbox)" step rather than pretending a real
  Mobile Money webhook fired, so the mismatch with a future real integration
  is obvious.

## Known gaps / next steps

- Push notifications (FCM/OneSignal) are not wired up — the spec marks this
  optional ("seulement si le temps le permet"); only in-app notifications
  (polling `GET /notifications`) are implemented.
- No withdrawal ("retrait") screen — the backend doesn't expose a withdrawal
  endpoint yet either (topups/deposits only), so there was nothing to call.
- No automated instrumentation/unit tests yet (the backend's 79 pytest tests
  cover the business logic these screens call).
