package com.nasrcash.app.ui.onboarding

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nasrcash.app.core.network.ApiResult
import com.nasrcash.app.data.repository.AuthRepository
import com.nasrcash.app.ui.common.UiState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.util.UUID

class OtpViewModel(private val authRepository: AuthRepository) : ViewModel() {

    private val _state = MutableStateFlow<UiState<Unit>>(UiState.Idle)
    val state: StateFlow<UiState<Unit>> = _state

    private val deviceId = UUID.randomUUID().toString()

    fun verify(phone: String, code: String) {
        if (code.length != 6) {
            _state.value = UiState.Error("Le code doit contenir 6 chiffres")
            return
        }
        _state.value = UiState.Loading
        viewModelScope.launch {
            when (val result = authRepository.verifyOtp(phone, code, deviceId)) {
                is ApiResult.Success -> _state.value = UiState.Success(Unit)
                is ApiResult.Error -> _state.value = UiState.Error(result.message)
            }
        }
    }
}
