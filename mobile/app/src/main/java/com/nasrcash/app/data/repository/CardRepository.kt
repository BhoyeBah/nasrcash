package com.nasrcash.app.data.repository

import com.nasrcash.app.core.network.ApiResult
import com.nasrcash.app.core.network.ApiService
import com.nasrcash.app.core.network.CardBalanceResponse
import com.nasrcash.app.core.network.CardFundRequest
import com.nasrcash.app.core.network.CardPaymentResponse
import com.nasrcash.app.core.network.CardResponse
import com.nasrcash.app.core.network.safeApiCall
import java.util.UUID

class CardRepository(private val apiService: ApiService) {

    suspend fun listCards(): ApiResult<List<CardResponse>> = safeApiCall { apiService.listCards() }

    suspend fun issueCard(): ApiResult<CardResponse> = safeApiCall { apiService.issueCard() }

    suspend fun getCard(cardId: String): ApiResult<CardResponse> = safeApiCall { apiService.getCard(cardId) }

    suspend fun getBalance(cardId: String): ApiResult<CardBalanceResponse> =
        safeApiCall { apiService.getCardBalance(cardId) }

    suspend fun freeze(cardId: String): ApiResult<CardResponse> = safeApiCall { apiService.freezeCard(cardId) }

    suspend fun unfreeze(cardId: String): ApiResult<CardResponse> = safeApiCall { apiService.unfreezeCard(cardId) }

    suspend fun close(cardId: String): ApiResult<CardResponse> = safeApiCall { apiService.closeCard(cardId) }

    suspend fun fund(cardId: String, amount: String): ApiResult<CardBalanceResponse> = safeApiCall {
        // A fresh key per user action — replaying the same tap never double-charges.
        apiService.fundCard(cardId, CardFundRequest(amount, UUID.randomUUID().toString()))
    }

    suspend fun getPayments(cardId: String): ApiResult<List<CardPaymentResponse>> =
        safeApiCall { apiService.getCardPayments(cardId) }
}
