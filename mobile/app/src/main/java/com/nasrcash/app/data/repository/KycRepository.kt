package com.nasrcash.app.data.repository

import com.nasrcash.app.core.network.ApiResult
import com.nasrcash.app.core.network.ApiService
import com.nasrcash.app.core.network.KycDocumentResponse
import com.nasrcash.app.core.network.KycProfileResponse
import com.nasrcash.app.core.network.KycStatusResponse
import com.nasrcash.app.core.network.safeApiCall
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.toRequestBody

class KycRepository(private val apiService: ApiService) {

    suspend fun start(): ApiResult<KycProfileResponse> = safeApiCall { apiService.startKyc() }

    suspend fun getStatus(): ApiResult<KycStatusResponse> = safeApiCall { apiService.getKycStatus() }

    suspend fun submit(): ApiResult<KycProfileResponse> = safeApiCall { apiService.submitKyc() }

    suspend fun uploadDocument(
        documentType: String,
        fileName: String,
        mimeType: String,
        bytes: ByteArray,
    ): ApiResult<KycDocumentResponse> = safeApiCall {
        val documentTypePart = documentType.toRequestBody("text/plain".toMediaType())
        val filePart = MultipartBody.Part.createFormData(
            "file",
            fileName,
            bytes.toRequestBody(mimeType.toMediaType()),
        )
        apiService.uploadKycDocument(documentTypePart, filePart)
    }
}
