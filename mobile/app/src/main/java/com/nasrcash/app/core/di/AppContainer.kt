package com.nasrcash.app.core.di

import android.content.Context
import com.nasrcash.app.core.network.NetworkModule
import com.nasrcash.app.core.session.TokenStore
import com.nasrcash.app.data.local.NasrCashDatabase
import com.nasrcash.app.data.repository.AuthRepository
import com.nasrcash.app.data.repository.CardRepository
import com.nasrcash.app.data.repository.KycRepository
import com.nasrcash.app.data.repository.NotificationRepository
import com.nasrcash.app.data.repository.WalletRepository

/**
 * Manual, no-framework dependency container. A ViewModelProvider.Factory in
 * each feature reaches into this to build its ViewModel — see
 * ui/common/ViewModelFactory.kt. Deliberately not Hilt/Koin: keeps the whole
 * wiring in one file that's easy to read end-to-end.
 */
class AppContainer(context: Context) {
    private val tokenStore = TokenStore(context)
    private val apiService = NetworkModule.createApiService(tokenStore)
    private val database = NasrCashDatabase.getInstance(context)

    val authRepository = AuthRepository(apiService, tokenStore)
    val walletRepository = WalletRepository(apiService)
    val cardRepository = CardRepository(apiService)
    val kycRepository = KycRepository(apiService)
    val notificationRepository = NotificationRepository(apiService, database.notificationDao())

    val isLoggedIn get() = authRepository.isLoggedIn
}
