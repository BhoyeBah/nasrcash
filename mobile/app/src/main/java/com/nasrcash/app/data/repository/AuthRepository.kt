package com.nasrcash.app.data.repository

import com.nasrcash.app.core.network.ApiResult
import com.nasrcash.app.core.network.ApiService
import com.nasrcash.app.core.network.LoginRequest
import com.nasrcash.app.core.network.LogoutRequest
import com.nasrcash.app.core.network.RegisterRequest
import com.nasrcash.app.core.network.RegisterResponse
import com.nasrcash.app.core.network.VerifyOtpRequest
import com.nasrcash.app.core.network.safeApiCall
import com.nasrcash.app.core.session.TokenStore

/**
 * The single place that knows how to turn a phone+PIN into a session.
 * ViewModels depend on this, never on [ApiService] or [TokenStore] directly.
 */
class AuthRepository(
    private val apiService: ApiService,
    private val tokenStore: TokenStore,
) {
    suspend fun register(phone: String, countryCode: String, pin: String): ApiResult<RegisterResponse> =
        safeApiCall { apiService.register(RegisterRequest(phone, countryCode, pin)) }

    suspend fun verifyOtp(phone: String, code: String, deviceId: String?): ApiResult<Unit> =
        safeApiCall {
            val tokens = apiService.verifyOtp(VerifyOtpRequest(phone, code, deviceId))
            tokenStore.saveTokens(tokens.access_token, tokens.refresh_token)
        }

    suspend fun login(phone: String, pin: String, deviceId: String?): ApiResult<Unit> =
        safeApiCall {
            val tokens = apiService.login(LoginRequest(phone, pin, deviceId))
            tokenStore.saveTokens(tokens.access_token, tokens.refresh_token)
        }

    suspend fun logout(): ApiResult<Unit> {
        val refreshToken = tokenStore.refreshToken
        val result = if (refreshToken != null) {
            safeApiCall { apiService.logout(LogoutRequest(refreshToken)) }
        } else {
            ApiResult.Success(Unit)
        }
        tokenStore.clear()
        return when (result) {
            is ApiResult.Success -> ApiResult.Success(Unit)
            is ApiResult.Error -> ApiResult.Success(Unit) // local session is cleared regardless
        }
    }

    val isLoggedIn get() = tokenStore.isLoggedIn
}
