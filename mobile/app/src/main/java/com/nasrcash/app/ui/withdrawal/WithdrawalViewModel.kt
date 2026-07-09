package com.nasrcash.app.ui.withdrawal

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nasrcash.app.core.network.ApiResult
import com.nasrcash.app.core.network.WithdrawalResponse
import com.nasrcash.app.data.repository.WalletRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

sealed interface WithdrawalScreenState {
    data object Form : WithdrawalScreenState
    data object Submitting : WithdrawalScreenState
    /** Mirrors the backend's real state machine: pending until the sandbox
     * "provider" confirms the payout, exactly like a Mobile Money webhook would. */
    data class PendingConfirmation(val withdrawal: WithdrawalResponse) : WithdrawalScreenState
    data object Confirming : WithdrawalScreenState
    data class Completed(val withdrawal: WithdrawalResponse) : WithdrawalScreenState
    data class Error(val message: String) : WithdrawalScreenState
}

val WITHDRAWAL_PROVIDERS = listOf(
    "orange_money" to "Orange Money",
    "mtn_momo" to "MTN MoMo",
    "moov_money" to "Moov Money",
)

class WithdrawalViewModel(
    private val walletRepository: WalletRepository,
    private val walletId: String,
) : ViewModel() {

    private val _state = MutableStateFlow<WithdrawalScreenState>(WithdrawalScreenState.Form)
    val state: StateFlow<WithdrawalScreenState> = _state

    fun initiate(amount: String, providerName: String) {
        if (amount.toDoubleOrNull() == null || amount.toDouble() <= 0) {
            _state.value = WithdrawalScreenState.Error("Montant invalide")
            return
        }
        _state.value = WithdrawalScreenState.Submitting
        viewModelScope.launch {
            when (val result = walletRepository.initiateWithdrawal(walletId, amount, providerName)) {
                is ApiResult.Success -> _state.value = WithdrawalScreenState.PendingConfirmation(result.data)
                is ApiResult.Error -> _state.value = WithdrawalScreenState.Error(result.message)
            }
        }
    }

    fun confirmSandboxSuccess(withdrawalId: String) {
        _state.value = WithdrawalScreenState.Confirming
        viewModelScope.launch {
            when (val result = walletRepository.simulateWithdrawalSuccess(withdrawalId)) {
                is ApiResult.Success -> _state.value = WithdrawalScreenState.Completed(result.data)
                is ApiResult.Error -> _state.value = WithdrawalScreenState.Error(result.message)
            }
        }
    }

    fun reset() {
        _state.value = WithdrawalScreenState.Form
    }
}
