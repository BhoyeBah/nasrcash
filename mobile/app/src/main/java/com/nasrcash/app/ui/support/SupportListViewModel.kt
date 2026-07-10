package com.nasrcash.app.ui.support

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nasrcash.app.core.network.ApiResult
import com.nasrcash.app.core.network.TicketResponse
import com.nasrcash.app.data.repository.SupportRepository
import com.nasrcash.app.ui.common.UiState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class SupportListViewModel(private val supportRepository: SupportRepository) : ViewModel() {

    private val _state = MutableStateFlow<UiState<List<TicketResponse>>>(UiState.Loading)
    val state: StateFlow<UiState<List<TicketResponse>>> = _state

    private val _actionError = MutableStateFlow<String?>(null)
    val actionError: StateFlow<String?> = _actionError

    private val _creating = MutableStateFlow(false)
    val creating: StateFlow<Boolean> = _creating

    init {
        load()
    }

    fun load() {
        _state.value = UiState.Loading
        viewModelScope.launch {
            when (val result = supportRepository.listTickets()) {
                is ApiResult.Success -> _state.value = UiState.Success(result.data)
                is ApiResult.Error -> _state.value = UiState.Error(result.message)
            }
        }
    }

    fun createTicket(subject: String, category: String, message: String, onCreated: (String) -> Unit) {
        if (subject.isBlank() || message.isBlank()) {
            _actionError.value = "Sujet et message sont requis"
            return
        }
        _actionError.value = null
        _creating.value = true
        viewModelScope.launch {
            when (val result = supportRepository.createTicket(subject, category, message)) {
                is ApiResult.Success -> {
                    load()
                    onCreated(result.data.id)
                }
                is ApiResult.Error -> _actionError.value = result.message
            }
            _creating.value = false
        }
    }

    fun clearActionError() {
        _actionError.value = null
    }
}
