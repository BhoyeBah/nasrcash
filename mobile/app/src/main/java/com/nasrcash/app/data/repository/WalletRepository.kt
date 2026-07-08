package com.nasrcash.app.data.repository

import com.nasrcash.app.core.network.ApiResult
import com.nasrcash.app.core.network.ApiService
import com.nasrcash.app.core.network.LedgerEntryResponse
import com.nasrcash.app.core.network.TopupRequest
import com.nasrcash.app.core.network.TopupResponse
import com.nasrcash.app.core.network.WalletBalanceResponse
import com.nasrcash.app.core.network.WalletResponse
import com.nasrcash.app.core.network.safeApiCall

class WalletRepository(private val apiService: ApiService) {

    suspend fun getPrimaryWallet(): ApiResult<WalletResponse> = safeApiCall {
        apiService.listWallets().first()
    }

    suspend fun getBalance(walletId: String): ApiResult<WalletBalanceResponse> =
        safeApiCall { apiService.getWalletBalance(walletId) }

    suspend fun getTransactions(walletId: String): ApiResult<List<LedgerEntryResponse>> =
        safeApiCall { apiService.getWalletTransactions(walletId) }

    suspend fun initiateTopup(walletId: String, amount: String, providerName: String): ApiResult<TopupResponse> =
        safeApiCall { apiService.createTopup(walletId, TopupRequest(amount, providerName)) }

    suspend fun listTopups(): ApiResult<List<TopupResponse>> = safeApiCall { apiService.listTopups() }

    suspend fun getTopup(topupId: String): ApiResult<TopupResponse> =
        safeApiCall { apiService.getTopup(topupId) }

    /** Sandbox-only confirmation, standing in for the provider's webhook. */
    suspend fun simulateTopupSuccess(topupId: String): ApiResult<TopupResponse> =
        safeApiCall { apiService.simulateTopupSuccess(topupId) }
}
