package com.nasrcash.app.ui.support

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nasrcash.app.core.network.ApiResult
import com.nasrcash.app.core.network.TicketMessageResponse
import com.nasrcash.app.core.network.TicketResponse
import com.nasrcash.app.data.repository.SupportRepository
import com.nasrcash.app.ui.common.UiState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

data class TicketDetailData(val ticket: TicketResponse, val messages: List<TicketMessageResponse>)

class SupportDetailViewModel(
    private val supportRepository: SupportRepository,
    private val ticketId: String,
) : ViewModel() {

    private val _state = MutableStateFlow<UiState<TicketDetailData>>(UiState.Loading)
    val state: StateFlow<UiState<TicketDetailData>> = _state

    private val _actionError = MutableStateFlow<String?>(null)
    val actionError: StateFlow<String?> = _actionError

    private val _sending = MutableStateFlow(false)
    val sending: StateFlow<Boolean> = _sending

    init {
        load()
    }

    fun load() {
        _state.value = UiState.Loading
        viewModelScope.launch {
            when (val result = supportRepository.getTicket(ticketId)) {
                is ApiResult.Success -> _state.value =
                    UiState.Success(TicketDetailData(result.data.ticket, result.data.messages))
                is ApiResult.Error -> _state.value = UiState.Error(result.message)
            }
        }
    }

    fun sendReply(body: String) {
        if (body.isBlank()) return
        _actionError.value = null
        _sending.value = true
        viewModelScope.launch {
            when (val result = supportRepository.addMessage(ticketId, body)) {
                is ApiResult.Success -> load()
                is ApiResult.Error -> _actionError.value = result.message
            }
            _sending.value = false
        }
    }
}
