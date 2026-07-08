package com.nasrcash.app.ui.history

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nasrcash.app.core.network.ApiResult
import com.nasrcash.app.core.network.LedgerEntryResponse
import com.nasrcash.app.data.repository.WalletRepository
import com.nasrcash.app.ui.common.UiState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class HistoryViewModel(
    private val walletRepository: WalletRepository,
    private val walletId: String,
) : ViewModel() {

    private val _state = MutableStateFlow<UiState<List<LedgerEntryResponse>>>(UiState.Loading)
    val state: StateFlow<UiState<List<LedgerEntryResponse>>> = _state

    init {
        load()
    }

    fun load() {
        _state.value = UiState.Loading
        viewModelScope.launch {
            when (val result = walletRepository.getTransactions(walletId)) {
                is ApiResult.Success -> _state.value = UiState.Success(result.data)
                is ApiResult.Error -> _state.value = UiState.Error(result.message)
            }
        }
    }
}
