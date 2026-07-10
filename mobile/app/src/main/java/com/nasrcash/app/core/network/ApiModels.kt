package com.nasrcash.app.core.network

import kotlinx.serialization.Serializable

// Mirrors app/modules/auth/schemas.py on the backend.

@Serializable
data class RegisterRequest(val phone: String, val country_code: String, val pin: String)

@Serializable
data class RegisterResponse(
    val user_id: String,
    val phone: String,
    val otp_expires_in_seconds: Int,
    val sandbox_otp_code: String? = null,
)

@Serializable
data class VerifyOtpRequest(
    val phone: String,
    val code: String,
    val device_id: String? = null,
    val device_name: String? = null,
)

@Serializable
data class LoginRequest(
    val phone: String,
    val pin: String,
    val device_id: String? = null,
    val device_name: String? = null,
)

@Serializable
data class RefreshRequest(val refresh_token: String)

@Serializable
data class LogoutRequest(val refresh_token: String, val all_devices: Boolean = false)

@Serializable
data class TokenPairResponse(val access_token: String, val refresh_token: String, val token_type: String = "bearer")

@Serializable
data class MessageResponse(val message: String)

// wallets

@Serializable
data class WalletResponse(val id: String, val country_code: String, val currency_code: String, val status: String)

@Serializable
data class WalletBalanceResponse(val wallet_id: String, val currency_code: String, val available_balance: String)

@Serializable
data class LedgerEntryResponse(
    val id: String,
    val direction: String,
    val amount: String,
    val currency: String,
    val description: String? = null,
    val created_at: String,
)

// topups

@Serializable
data class TopupRequest(val amount: String, val provider_name: String)

@Serializable
data class TopupResponse(
    val id: String,
    val wallet_id: String,
    val amount: String,
    val fee_amount: String,
    val net_amount: String,
    val currency_code: String,
    val provider_name: String,
    val status: String,
    val failure_reason: String? = null,
    val confirmed_at: String? = null,
    val created_at: String,
)

// withdrawals

@Serializable
data class WithdrawalRequest(val amount: String, val provider_name: String)

@Serializable
data class WithdrawalResponse(
    val id: String,
    val wallet_id: String,
    val amount: String,
    val fee_amount: String,
    val net_amount: String,
    val currency_code: String,
    val provider_name: String,
    val status: String,
    val failure_reason: String? = null,
    val confirmed_at: String? = null,
    val created_at: String,
)

// KYC

@Serializable
data class KycProfileResponse(
    val id: String,
    val level_requested: Int,
    val status: String,
    val rejection_reason: String? = null,
    val submitted_at: String? = null,
    val reviewed_at: String? = null,
)

@Serializable
data class KycDocumentResponse(val id: String, val document_type: String, val original_filename: String)

@Serializable
data class KycStatusResponse(
    val profile: KycProfileResponse? = null,
    val documents: List<KycDocumentResponse> = emptyList(),
    val current_kyc_level: Int,
)

// cards

@Serializable
data class CardResponse(
    val id: String,
    val masked_pan: String,
    val last4: String,
    val brand: String,
    val displayed_currency: String,
    val status: String,
    val nickname: String? = null,
    val expiry_month: Int,
    val expiry_year: Int,
)

@Serializable
data class CardBalanceResponse(val card_id: String, val currency_code: String, val available_balance: String)

@Serializable
data class CardFundRequest(val amount: String, val idempotency_key: String)

@Serializable
data class CardPaymentResponse(
    val id: String,
    val card_id: String,
    val merchant_name: String,
    val merchant_currency: String,
    val merchant_amount: String,
    val fx_rate: String,
    val local_currency: String,
    val local_amount: String,
    val fees_amount: String,
    val total_debited: String,
    val status: String,
    val decline_reason: String? = null,
    val provider_reference: String,
    val created_at: String,
)

// support

@Serializable
data class TicketCreateRequest(val subject: String, val category: String, val message: String)

@Serializable
data class MessageCreateRequest(val body: String)

@Serializable
data class TicketResponse(
    val id: String,
    val user_id: String,
    val subject: String,
    val category: String,
    val status: String,
    val created_at: String,
)

@Serializable
data class MessageResponse(
    val id: String,
    val ticket_id: String,
    val sender_type: String,
    val sender_id: String,
    val body: String,
    val created_at: String,
)

@Serializable
data class TicketDetailResponse(val ticket: TicketResponse, val messages: List<MessageResponse>)

// notifications

@Serializable
data class NotificationResponse(
    val id: String,
    val type: String,
    val title: String,
    val body: String,
    val read_at: String? = null,
    val created_at: String,
)

@Serializable
data class UnreadCountResponse(val unread_count: Int)

@Serializable
data class ApiErrorBody(val error_code: String, val message: String)
