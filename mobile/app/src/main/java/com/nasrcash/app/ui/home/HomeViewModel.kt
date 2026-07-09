package com.nasrcash.app.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nasrcash.app.core.network.ApiResult
import com.nasrcash.app.core.network.CardResponse
import com.nasrcash.app.core.network.WalletResponse
import com.nasrcash.app.data.repository.CardRepository
import com.nasrcash.app.data.repository.KycRepository
import com.nasrcash.app.data.repository.NotificationRepository
import com.nasrcash.app.data.repository.WalletRepository
import com.nasrcash.app.ui.common.UiState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

data class HomeData(
    val wallet: WalletResponse,
    val walletBalance: String,
    val cards: List<CardResponse>,
    val unreadNotifications: Int,
    val currentKycLevel: Int,
)

class HomeViewModel(
    private val walletRepository: WalletRepository,
    private val cardRepository: CardRepository,
    private val notificationRepository: NotificationRepository,
    private val kycRepository: KycRepository,
) : ViewModel() {

    private val _state = MutableStateFlow<UiState<HomeData>>(UiState.Loading)
    val state: StateFlow<UiState<HomeData>> = _state

    private val _actionError = MutableStateFlow<String?>(null)
    val actionError: StateFlow<String?> = _actionError

    private val _issuingCard = MutableStateFlow(false)
    val issuingCard: StateFlow<Boolean> = _issuingCard

    init {
        load()
    }

    fun load() {
        _state.value = UiState.Loading
        viewModelScope.launch {
            val walletResult = walletRepository.getPrimaryWallet()
            if (walletResult is ApiResult.Error) {
                _state.value = UiState.Error(walletResult.message)
                return@launch
            }
            val wallet = (walletResult as ApiResult.Success).data

            val balanceResult = walletRepository.getBalance(wallet.id)
            val balance = (balanceResult as? ApiResult.Success)?.data?.available_balance ?: "0.00"

            val cardsResult = cardRepository.listCards()
            val cards = (cardsResult as? ApiResult.Success)?.data ?: emptyList()

            val unreadResult = notificationRepository.getUnreadCount()
            val unread = (unreadResult as? ApiResult.Success)?.data ?: 0

            val kycResult = kycRepository.getStatus()
            val kycLevel = (kycResult as? ApiResult.Success)?.data?.current_kyc_level ?: 0

            _state.value = UiState.Success(HomeData(wallet, balance, cards, unread, kycLevel))
        }
    }

    fun issueCard() {
        _actionError.value = null
        _issuingCard.value = true
        viewModelScope.launch {
            when (val result = cardRepository.issueCard()) {
                is ApiResult.Success -> load()
                is ApiResult.Error -> _actionError.value = result.message
            }
            _issuingCard.value = false
        }
    }

    fun clearActionError() {
        _actionError.value = null
    }
}
