package com.nasrcash.app.core.network

import com.nasrcash.app.BuildConfig
import com.nasrcash.app.core.session.TokenStore
import kotlinx.serialization.json.Json
import okhttp3.Authenticator
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.Route
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.kotlinx.serialization.asConverterFactory

private val json = Json {
    ignoreUnknownKeys = true
    encodeDefaults = true
}

/** Attaches the current access token, if any, to every outgoing request. */
private class AuthInterceptor(private val tokenStore: TokenStore) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val original = chain.request()
        val token = tokenStore.accessToken
        val request = if (token != null) {
            original.newBuilder().header("Authorization", "Bearer $token").build()
        } else {
            original
        }
        return chain.proceed(request)
    }
}

/**
 * On a 401, tries once to refresh the access token using the stored refresh
 * token, via a bare OkHttp call (not through the authenticated client, to
 * avoid recursing back into this same authenticator).
 */
private class TokenAuthenticator(private val tokenStore: TokenStore) : Authenticator {
    private val refreshClient = OkHttpClient.Builder().build()

    override fun authenticate(route: Route?, response: Response): Request? {
        if (responseCount(response) >= 2) return null // already retried once, give up
        val refreshToken = tokenStore.refreshToken ?: return null

        val requestBody = json.encodeToString(RefreshRequest.serializer(), RefreshRequest(refreshToken))
            .toRequestBody("application/json".toMediaType())

        val refreshRequest = Request.Builder()
            .url("${BuildConfig.API_BASE_URL}api/v1/auth/refresh")
            .post(requestBody)
            .build()

        refreshClient.newCall(refreshRequest).execute().use { refreshResponse ->
            if (!refreshResponse.isSuccessful) {
                tokenStore.clear()
                return null
            }
            val body = refreshResponse.body?.string() ?: return null
            val tokens = json.decodeFromString(TokenPairResponse.serializer(), body)
            tokenStore.saveTokens(tokens.access_token, tokens.refresh_token)

            return response.request.newBuilder()
                .header("Authorization", "Bearer ${tokens.access_token}")
                .build()
        }
    }

    private fun responseCount(response: Response): Int {
        var count = 1
        var prior = response.priorResponse
        while (prior != null) {
            count++
            prior = prior.priorResponse
        }
        return count
    }
}

object NetworkModule {

    fun createApiService(tokenStore: TokenStore): ApiService {
        val logging = HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) {
                HttpLoggingInterceptor.Level.BASIC
            } else {
                HttpLoggingInterceptor.Level.NONE
            }
        }

        val client = OkHttpClient.Builder()
            .addInterceptor(AuthInterceptor(tokenStore))
            .authenticator(TokenAuthenticator(tokenStore))
            .addInterceptor(logging)
            .build()

        val contentType = "application/json".toMediaType()
        val retrofit = Retrofit.Builder()
            .baseUrl(BuildConfig.API_BASE_URL)
            .client(client)
            .addConverterFactory(json.asConverterFactory(contentType))
            .build()

        return retrofit.create(ApiService::class.java)
    }
}
