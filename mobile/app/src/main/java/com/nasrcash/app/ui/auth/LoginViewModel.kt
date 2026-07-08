package com.nasrcash.app.ui.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nasrcash.app.core.network.ApiResult
import com.nasrcash.app.data.repository.AuthRepository
import com.nasrcash.app.ui.common.UiState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.util.UUID

class LoginViewModel(private val authRepository: AuthRepository) : ViewModel() {

    private val _state = MutableStateFlow<UiState<Unit>>(UiState.Idle)
    val state: StateFlow<UiState<Unit>> = _state

    private val deviceId = UUID.randomUUID().toString()

    fun login(phone: String, pin: String) {
        if (phone.isBlank() || pin.isBlank()) {
            _state.value = UiState.Error("Numéro et PIN requis")
            return
        }
        _state.value = UiState.Loading
        viewModelScope.launch {
            when (val result = authRepository.login(phone, pin, deviceId)) {
                is ApiResult.Success -> _state.value = UiState.Success(Unit)
                is ApiResult.Error -> _state.value = UiState.Error(result.message)
            }
        }
    }
}
