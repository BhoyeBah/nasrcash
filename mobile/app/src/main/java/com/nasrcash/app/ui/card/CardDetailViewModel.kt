package com.nasrcash.app.ui.card

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nasrcash.app.core.network.ApiResult
import com.nasrcash.app.core.network.CardPaymentResponse
import com.nasrcash.app.core.network.CardResponse
import com.nasrcash.app.data.repository.CardRepository
import com.nasrcash.app.ui.common.UiState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

data class CardDetailData(
    val card: CardResponse,
    val balance: String,
    val payments: List<CardPaymentResponse>,
)

class CardDetailViewModel(
    private val cardRepository: CardRepository,
    private val cardId: String,
) : ViewModel() {

    private val _state = MutableStateFlow<UiState<CardDetailData>>(UiState.Loading)
    val state: StateFlow<UiState<CardDetailData>> = _state

    private val _actionError = MutableStateFlow<String?>(null)
    val actionError: StateFlow<String?> = _actionError

    private val _actionInProgress = MutableStateFlow(false)
    val actionInProgress: StateFlow<Boolean> = _actionInProgress

    init {
        load()
    }

    fun load() {
        _state.value = UiState.Loading
        viewModelScope.launch {
            val cardResult = cardRepository.getCard(cardId)
            if (cardResult is ApiResult.Error) {
                _state.value = UiState.Error(cardResult.message)
                return@launch
            }
            val card = (cardResult as ApiResult.Success).data

            val balanceResult = cardRepository.getBalance(cardId)
            if (balanceResult is ApiResult.Error) {
                _state.value = UiState.Error(balanceResult.message)
                return@launch
            }
            val balance = (balanceResult as ApiResult.Success).data.available_balance

            val paymentsResult = cardRepository.getPayments(cardId)
            val payments = (paymentsResult as? ApiResult.Success)?.data ?: emptyList()

            _state.value = UiState.Success(CardDetailData(card, balance, payments))
        }
    }

    fun fund(amount: String) {
        if (amount.toDoubleOrNull() == null || amount.toDouble() <= 0) {
            _actionError.value = "Montant invalide"
            return
        }
        _actionInProgress.value = true
        viewModelScope.launch {
            when (val result = cardRepository.fund(cardId, amount)) {
                is ApiResult.Success -> load()
                is ApiResult.Error -> _actionError.value = result.message
            }
            _actionInProgress.value = false
        }
    }

    fun freeze() = runCardAction { cardRepository.freeze(cardId) }
    fun unfreeze() = runCardAction { cardRepository.unfreeze(cardId) }
    fun close() = runCardAction { cardRepository.close(cardId) }

    private fun runCardAction(action: suspend () -> ApiResult<CardResponse>) {
        _actionInProgress.value = true
        viewModelScope.launch {
            when (val result = action()) {
                is ApiResult.Success -> load()
                is ApiResult.Error -> _actionError.value = result.message
            }
            _actionInProgress.value = false
        }
    }

    fun clearActionError() {
        _actionError.value = null
    }
}
