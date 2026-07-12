package com.nasrcash.app.core.network

import okhttp3.MultipartBody

private fun notStubbed(name: String): Nothing =
    throw NotImplementedError("FakeApiService.$name was called without being stubbed")

/**
 * Hand-rolled [ApiService] test double. Only the handful of endpoints each
 * test actually exercises are wired to a lambda; everything else throws so a
 * test silently relying on an unstubbed call fails loudly instead of NPEing.
 */
class FakeApiService(
    val listWalletsResult: suspend () -> List<WalletResponse> = { notStubbed("listWallets") },
    val getWalletBalanceResult: suspend (String) -> WalletBalanceResponse = { notStubbed("getWalletBalance") },
    val listCardsResult: suspend () -> List<CardResponse> = { notStubbed("listCards") },
    val issueCardResult: suspend () -> CardResponse = { notStubbed("issueCard") },
    val getUnreadNotificationCountResult: suspend () -> UnreadCountResponse = { notStubbed("getUnreadNotificationCount") },
    val getKycStatusResult: suspend () -> KycStatusResponse = { notStubbed("getKycStatus") },
    val createTicketResult: suspend (TicketCreateRequest) -> TicketResponse = { notStubbed("createTicket") },
    val listTicketsResult: suspend () -> List<TicketResponse> = { notStubbed("listTickets") },
) : ApiService {

    override suspend fun register(body: RegisterRequest): RegisterResponse = notStubbed("register")
    override suspend fun verifyOtp(body: VerifyOtpRequest): TokenPairResponse = notStubbed("verifyOtp")
    override suspend fun login(body: LoginRequest): TokenPairResponse = notStubbed("login")
    override suspend fun refresh(body: RefreshRequest): TokenPairResponse = notStubbed("refresh")
    override suspend fun logout(body: LogoutRequest): MessageResponse = notStubbed("logout")

    override suspend fun listWallets(): List<WalletResponse> = listWalletsResult()
    override suspend fun getWalletBalance(walletId: String): WalletBalanceResponse = getWalletBalanceResult(walletId)
    override suspend fun getWalletTransactions(walletId: String): List<LedgerEntryResponse> =
        notStubbed("getWalletTransactions")

    override suspend fun createTopup(walletId: String, body: TopupRequest): TopupResponse = notStubbed("createTopup")
    override suspend fun listTopups(): List<TopupResponse> = notStubbed("listTopups")
    override suspend fun getTopup(topupId: String): TopupResponse = notStubbed("getTopup")
    override suspend fun simulateTopupSuccess(topupId: String): TopupResponse = notStubbed("simulateTopupSuccess")

    override suspend fun createWithdrawal(walletId: String, body: WithdrawalRequest): WithdrawalResponse =
        notStubbed("createWithdrawal")

    override suspend fun listWithdrawals(): List<WithdrawalResponse> = notStubbed("listWithdrawals")
    override suspend fun getWithdrawal(withdrawalId: String): WithdrawalResponse = notStubbed("getWithdrawal")
    override suspend fun simulateWithdrawalSuccess(withdrawalId: String): WithdrawalResponse =
        notStubbed("simulateWithdrawalSuccess")

    override suspend fun startKyc(): KycProfileResponse = notStubbed("startKyc")
    override suspend fun uploadKycDocument(
        documentType: okhttp3.RequestBody,
        file: MultipartBody.Part,
    ): KycDocumentResponse = notStubbed("uploadKycDocument")

    override suspend fun submitKyc(): KycProfileResponse = notStubbed("submitKyc")
    override suspend fun getKycStatus(): KycStatusResponse = getKycStatusResult()

    override suspend fun issueCard(): CardResponse = issueCardResult()
    override suspend fun listCards(): List<CardResponse> = listCardsResult()
    override suspend fun getCard(cardId: String): CardResponse = notStubbed("getCard")
    override suspend fun getCardBalance(cardId: String): CardBalanceResponse = notStubbed("getCardBalance")
    override suspend fun fundCard(cardId: String, body: CardFundRequest): CardBalanceResponse =
        notStubbed("fundCard")

    override suspend fun freezeCard(cardId: String): CardResponse = notStubbed("freezeCard")
    override suspend fun unfreezeCard(cardId: String): CardResponse = notStubbed("unfreezeCard")
    override suspend fun closeCard(cardId: String): CardResponse = notStubbed("closeCard")
    override suspend fun getCardTransactions(cardId: String): List<LedgerEntryResponse> =
        notStubbed("getCardTransactions")

    override suspend fun getCardPayments(cardId: String): List<CardPaymentResponse> =
        notStubbed("getCardPayments")

    override suspend fun createTicket(body: TicketCreateRequest): TicketResponse = createTicketResult(body)
    override suspend fun listTickets(): List<TicketResponse> = listTicketsResult()
    override suspend fun getTicket(ticketId: String): TicketDetailResponse = notStubbed("getTicket")
    override suspend fun addTicketMessage(ticketId: String, body: MessageCreateRequest): TicketMessageResponse =
        notStubbed("addTicketMessage")

    override suspend fun listNotifications(unreadOnly: Boolean): List<NotificationResponse> =
        notStubbed("listNotifications")

    override suspend fun getUnreadNotificationCount(): UnreadCountResponse = getUnreadNotificationCountResult()
    override suspend fun markNotificationRead(notificationId: String): NotificationResponse =
        notStubbed("markNotificationRead")
}
