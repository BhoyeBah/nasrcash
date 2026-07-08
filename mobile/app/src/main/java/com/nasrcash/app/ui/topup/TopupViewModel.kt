package com.nasrcash.app.ui.topup

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nasrcash.app.core.network.ApiResult
import com.nasrcash.app.core.network.TopupResponse
import com.nasrcash.app.data.repository.WalletRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

sealed interface TopupScreenState {
    data object Form : TopupScreenState
    data object Submitting : TopupScreenState
    /** Mirrors the backend's real state machine: pending until the sandbox
     * "provider" confirms it, exactly like the mobile money webhook would. */
    data class PendingConfirmation(val topup: TopupResponse) : TopupScreenState
    data object Confirming : TopupScreenState
    data class Completed(val topup: TopupResponse) : TopupScreenState
    data class Error(val message: String) : TopupScreenState
}

val TOPUP_PROVIDERS = listOf("orange_money" to "Orange Money", "mtn_momo" to "MTN MoMo", "moov_money" to "Moov Money")

class TopupViewModel(
    private val walletRepository: WalletRepository,
    private val walletId: String,
) : ViewModel() {

    private val _state = MutableStateFlow<TopupScreenState>(TopupScreenState.Form)
    val state: StateFlow<TopupScreenState> = _state

    fun initiate(amount: String, providerName: String) {
        if (amount.toDoubleOrNull() == null || amount.toDouble() <= 0) {
            _state.value = TopupScreenState.Error("Montant invalide")
            return
        }
        _state.value = TopupScreenState.Submitting
        viewModelScope.launch {
            when (val result = walletRepository.initiateTopup(walletId, amount, providerName)) {
                is ApiResult.Success -> _state.value = TopupScreenState.PendingConfirmation(result.data)
                is ApiResult.Error -> _state.value = TopupScreenState.Error(result.message)
            }
        }
    }

    fun confirmSandboxSuccess(topupId: String) {
        _state.value = TopupScreenState.Confirming
        viewModelScope.launch {
            when (val result = walletRepository.simulateTopupSuccess(topupId)) {
                is ApiResult.Success -> _state.value = TopupScreenState.Completed(result.data)
                is ApiResult.Error -> _state.value = TopupScreenState.Error(result.message)
            }
        }
    }

    fun reset() {
        _state.value = TopupScreenState.Form
    }
}
