package com.nasrcash.app.core.network

import kotlinx.serialization.json.Json
import retrofit2.HttpException

sealed interface ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>
    data class Error(val message: String, val errorCode: String? = null) : ApiResult<Nothing>
}

private val errorJson = Json { ignoreUnknownKeys = true }

/**
 * Wraps a suspend API call, translating network/HTTP failures into a
 * [ApiResult.Error] so ViewModels never need a try/catch around Retrofit calls.
 */
suspend fun <T> safeApiCall(block: suspend () -> T): ApiResult<T> = try {
    ApiResult.Success(block())
} catch (e: HttpException) {
    val body = e.response()?.errorBody()?.string()
    val parsed = body?.let {
        runCatching { errorJson.decodeFromString(ApiErrorBody.serializer(), it) }.getOrNull()
    }
    ApiResult.Error(parsed?.message ?: "Erreur serveur (${e.code()})", parsed?.error_code)
} catch (e: java.io.IOException) {
    ApiResult.Error("Impossible de contacter le serveur — vérifiez votre connexion")
} catch (e: Exception) {
    ApiResult.Error(e.message ?: "Erreur inattendue")
}
