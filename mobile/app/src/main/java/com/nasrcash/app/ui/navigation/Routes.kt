package com.nasrcash.app.ui.navigation

object Routes {
    const val REGISTER = "register"
    const val OTP = "otp/{phone}"
    const val LOGIN = "login"
    const val HOME = "home"
    const val TOPUP = "topup"
    const val WITHDRAWAL = "withdrawal"
    const val KYC = "kyc"
    const val CARD_DETAIL = "card/{cardId}"
    const val HISTORY = "history/{walletId}"
    const val NOTIFICATIONS = "notifications"

    fun otp(phone: String) = "otp/${Uri.encode(phone)}"
    fun cardDetail(cardId: String) = "card/$cardId"
    fun history(walletId: String) = "history/$walletId"
}

// Minimal encode helper to avoid pulling in android.net.Uri in a non-Android-context file.
private object Uri {
    fun encode(value: String): String = java.net.URLEncoder.encode(value, "UTF-8")
}
