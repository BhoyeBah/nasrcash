package com.nasrcash.app.ui.kyc

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nasrcash.app.core.network.ApiResult
import com.nasrcash.app.core.network.KycStatusResponse
import com.nasrcash.app.data.repository.KycRepository
import com.nasrcash.app.ui.common.UiState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class KycViewModel(private val kycRepository: KycRepository) : ViewModel() {

    private val _state = MutableStateFlow<UiState<KycStatusResponse>>(UiState.Loading)
    val state: StateFlow<UiState<KycStatusResponse>> = _state

    private val _actionError = MutableStateFlow<String?>(null)
    val actionError: StateFlow<String?> = _actionError

    private val _uploadingType = MutableStateFlow<String?>(null)
    val uploadingType: StateFlow<String?> = _uploadingType

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            when (val result = kycRepository.getStatus()) {
                is ApiResult.Success -> _state.value = UiState.Success(result.data)
                is ApiResult.Error -> _state.value = UiState.Error(result.message)
            }
        }
    }

    fun start() {
        viewModelScope.launch {
            when (val result = kycRepository.start()) {
                is ApiResult.Success -> refresh()
                is ApiResult.Error -> _actionError.value = result.message
            }
        }
    }

    fun uploadDocument(documentType: String, fileName: String, mimeType: String, bytes: ByteArray) {
        _uploadingType.value = documentType
        viewModelScope.launch {
            when (val result = kycRepository.uploadDocument(documentType, fileName, mimeType, bytes)) {
                is ApiResult.Success -> refresh()
                is ApiResult.Error -> _actionError.value = result.message
            }
            _uploadingType.value = null
        }
    }

    fun submit() {
        viewModelScope.launch {
            when (val result = kycRepository.submit()) {
                is ApiResult.Success -> refresh()
                is ApiResult.Error -> _actionError.value = result.message
            }
        }
    }

    fun clearActionError() {
        _actionError.value = null
    }
}
