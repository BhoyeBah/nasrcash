package com.nasrcash.app.ui.onboarding

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nasrcash.app.core.network.ApiResult
import com.nasrcash.app.data.repository.AuthRepository
import com.nasrcash.app.ui.common.UiState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class RegisterViewModel(private val authRepository: AuthRepository) : ViewModel() {

    private val _state = MutableStateFlow<UiState<String>>(UiState.Idle) // Success carries the sandbox OTP code
    val state: StateFlow<UiState<String>> = _state

    fun register(phone: String, countryCode: String, pin: String) {
        if (phone.isBlank() || pin.length < 4) {
            _state.value = UiState.Error("Numéro et PIN (4 à 6 chiffres) requis")
            return
        }
        _state.value = UiState.Loading
        viewModelScope.launch {
            when (val result = authRepository.register(phone, countryCode, pin)) {
                is ApiResult.Success -> _state.value = UiState.Success(result.data.sandbox_otp_code ?: "")
                is ApiResult.Error -> _state.value = UiState.Error(result.message)
            }
        }
    }
}
