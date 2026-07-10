package com.nasrcash.app.core.network

import okhttp3.MultipartBody
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Path
import retrofit2.http.Query

/** Thin 1:1 mapping of the NasrCash backend's public API — see backend/app/modules/*/router.py. */
interface ApiService {

    // --- auth ---
    @POST("api/v1/auth/register")
    suspend fun register(@Body body: RegisterRequest): RegisterResponse

    @POST("api/v1/auth/verify-otp")
    suspend fun verifyOtp(@Body body: VerifyOtpRequest): TokenPairResponse

    @POST("api/v1/auth/login")
    suspend fun login(@Body body: LoginRequest): TokenPairResponse

    @POST("api/v1/auth/refresh")
    suspend fun refresh(@Body body: RefreshRequest): TokenPairResponse

    @POST("api/v1/auth/logout")
    suspend fun logout(@Body body: LogoutRequest): MessageResponse

    // --- wallets ---
    @GET("api/v1/wallets")
    suspend fun listWallets(): List<WalletResponse>

    @GET("api/v1/wallets/{walletId}/balance")
    suspend fun getWalletBalance(@Path("walletId") walletId: String): WalletBalanceResponse

    @GET("api/v1/wallets/{walletId}/transactions")
    suspend fun getWalletTransactions(@Path("walletId") walletId: String): List<LedgerEntryResponse>

    // --- topups ---
    @POST("api/v1/wallets/{walletId}/topup")
    suspend fun createTopup(@Path("walletId") walletId: String, @Body body: TopupRequest): TopupResponse

    @GET("api/v1/topups")
    suspend fun listTopups(): List<TopupResponse>

    @GET("api/v1/topups/{topupId}")
    suspend fun getTopup(@Path("topupId") topupId: String): TopupResponse

    // Sandbox-only — see backend/app/modules/sandbox. Stands in for the
    // Mobile Money provider webhook until a real partner is integrated.
    @POST("api/v1/sandbox/topups/{topupId}/simulate-success")
    suspend fun simulateTopupSuccess(@Path("topupId") topupId: String): TopupResponse

    // --- withdrawals ---
    @POST("api/v1/wallets/{walletId}/withdrawals")
    suspend fun createWithdrawal(
        @Path("walletId") walletId: String,
        @Body body: WithdrawalRequest,
    ): WithdrawalResponse

    @GET("api/v1/withdrawals")
    suspend fun listWithdrawals(): List<WithdrawalResponse>

    @GET("api/v1/withdrawals/{withdrawalId}")
    suspend fun getWithdrawal(@Path("withdrawalId") withdrawalId: String): WithdrawalResponse

    // Sandbox-only, same rationale as simulateTopupSuccess above.
    @POST("api/v1/sandbox/withdrawals/{withdrawalId}/simulate-success")
    suspend fun simulateWithdrawalSuccess(@Path("withdrawalId") withdrawalId: String): WithdrawalResponse

    // --- KYC ---
    @POST("api/v1/kyc/start")
    suspend fun startKyc(): KycProfileResponse

    @Multipart
    @POST("api/v1/kyc/documents")
    suspend fun uploadKycDocument(
        @Part("document_type") documentType: okhttp3.RequestBody,
        @Part file: MultipartBody.Part,
    ): KycDocumentResponse

    @POST("api/v1/kyc/submit")
    suspend fun submitKyc(): KycProfileResponse

    @GET("api/v1/kyc/status")
    suspend fun getKycStatus(): KycStatusResponse

    // --- cards ---
    @POST("api/v1/cards")
    suspend fun issueCard(): CardResponse

    @GET("api/v1/cards")
    suspend fun listCards(): List<CardResponse>

    @GET("api/v1/cards/{cardId}")
    suspend fun getCard(@Path("cardId") cardId: String): CardResponse

    @GET("api/v1/cards/{cardId}/balance")
    suspend fun getCardBalance(@Path("cardId") cardId: String): CardBalanceResponse

    @POST("api/v1/cards/{cardId}/fund")
    suspend fun fundCard(@Path("cardId") cardId: String, @Body body: CardFundRequest): CardBalanceResponse

    @POST("api/v1/cards/{cardId}/freeze")
    suspend fun freezeCard(@Path("cardId") cardId: String): CardResponse

    @POST("api/v1/cards/{cardId}/unfreeze")
    suspend fun unfreezeCard(@Path("cardId") cardId: String): CardResponse

    @POST("api/v1/cards/{cardId}/close")
    suspend fun closeCard(@Path("cardId") cardId: String): CardResponse

    @GET("api/v1/cards/{cardId}/transactions")
    suspend fun getCardTransactions(@Path("cardId") cardId: String): List<LedgerEntryResponse>

    @GET("api/v1/cards/{cardId}/payments")
    suspend fun getCardPayments(@Path("cardId") cardId: String): List<CardPaymentResponse>

    // --- support ---
    @POST("api/v1/support/tickets")
    suspend fun createTicket(@Body body: TicketCreateRequest): TicketResponse

    @GET("api/v1/support/tickets")
    suspend fun listTickets(): List<TicketResponse>

    @GET("api/v1/support/tickets/{ticketId}")
    suspend fun getTicket(@Path("ticketId") ticketId: String): TicketDetailResponse

    @POST("api/v1/support/tickets/{ticketId}/messages")
    suspend fun addTicketMessage(
        @Path("ticketId") ticketId: String,
        @Body body: MessageCreateRequest,
    ): MessageResponse

    // --- notifications ---
    @GET("api/v1/notifications")
    suspend fun listNotifications(@Query("unread_only") unreadOnly: Boolean = false): List<NotificationResponse>

    @GET("api/v1/notifications/unread-count")
    suspend fun getUnreadNotificationCount(): UnreadCountResponse

    @POST("api/v1/notifications/{notificationId}/read")
    suspend fun markNotificationRead(@Path("notificationId") notificationId: String): NotificationResponse
}
