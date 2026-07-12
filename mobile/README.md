# NasrCash Mobile (Android)

Kotlin + Jetpack Compose client for the NasrCash sandbox MVP — onboarding/OTP,
PIN + biometric unlock, wallet overview, deposits and withdrawals, KYC
document upload, virtual card management, transaction history, and
notifications. See
`../CAHIER_DES_CHARGES_NASRCASH.md` and `../NASRCASH_TECH_SPEC.md` for the
full product and technical specification.

## ✅ Build status

`./gradlew assembleDebug` and `./gradlew testDebugUnitTest` both pass (9 unit
tests, `ui/home` and `ui/support` ViewModels, via a hand-rolled `FakeApiService`).
This was verified in a sandbox with an Android SDK (platform 34, build-tools
34.0.0) but **no emulator or physical device available** (no `/dev/kvm`, no
virtualization CPU flags in that container) — so the app has never actually
been run and its UI/navigation has not been exercised end-to-end. Getting it
onto a real emulator or device (see below) and walking the golden path
(register → OTP → KYC → issue card → topup/withdrawal → support ticket) is
the next real gap to close.

## Stack

Kotlin · Jetpack Compose · Material 3 · Navigation Compose · Retrofit +
kotlinx.serialization · Room (local cache) · EncryptedSharedPreferences ·
androidx.biometric

## Running locally

Prerequisites: Android Studio (bundles a compatible JDK) or a standalone
Android SDK + JDK 17+. No global Gradle install needed — `./gradlew` bundled
in this repo downloads the right Gradle version (8.14.3) on first run.

1. **Start the backend** (needs Postgres + Redis):

   ```bash
   cd ../backend
   docker compose up -d postgres redis
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

2. **Open `mobile/` in Android Studio** and let Gradle sync (first sync
   downloads AGP/Kotlin/Compose/AndroidX — can take a few minutes). Or from
   a terminal: `./gradlew assembleDebug`.

3. **Run on an emulator** (AVD Manager → create a device, any API 26+) or a
   **physical device** (enable USB debugging, plug in via USB).
   - Emulator: no config needed — it already reaches the host's `localhost`
     via `10.0.2.2` (see `API_BASE_URL` in `app/build.gradle.kts`).
   - Physical device on the same network: change `API_BASE_URL` to your
     machine's LAN IP (`http://192.168.x.x:8000/`), or run
     `adb reverse tcp:8000 tcp:8000` to forward the device's `localhost:8000`
     to your machine instead.

4. Hit the green Run button in Android Studio, or `./gradlew installDebug`
   then launch the app manually. No real SMS is sent in sandbox mode — the
   OTP screen tells you to check the server logs, and that's literal: the
   backend logs `[SANDBOX OTP] phone=... code=...` to its own terminal
   output on every register/login, so just read the code from the terminal
   where `uvicorn` is running and type it in.

5. **Run the unit tests**: `./gradlew testDebugUnitTest` (or via Android
   Studio's test runner on `app/src/test`).

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
- **Sandbox is explicit in the UI**, not hidden: the topup and withdrawal
  screens both show a distinct "pending → confirm (sandbox)" step rather than
  pretending a real Mobile Money webhook fired, so the mismatch with a future
  real integration is obvious.

## Known gaps / next steps

- Push notifications (FCM/OneSignal) are not wired up — the spec marks this
  optional ("seulement si le temps le permet"); only in-app notifications
  (polling `GET /notifications`) are implemented.
- Unit test coverage (`app/src/test`) currently covers `HomeViewModel` and
  `SupportListViewModel` only. Extend to the rest (topup, withdrawal, cards,
  KYC) by reusing `FakeApiService` — most of the boilerplate is already there.
- No instrumented/UI tests (`app/src/androidTest`) — would need a real device
  or emulator to run, which no environment has had access to yet.
