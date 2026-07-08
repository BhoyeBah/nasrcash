package com.nasrcash.app.ui.notifications

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nasrcash.app.data.repository.NotificationRepository
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class NotificationsViewModel(private val notificationRepository: NotificationRepository) : ViewModel() {

    val notifications: StateFlow<List<com.nasrcash.app.core.network.NotificationResponse>> =
        notificationRepository.observeCached()
            .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch { notificationRepository.refresh() }
    }

    fun markRead(notificationId: String) {
        viewModelScope.launch { notificationRepository.markRead(notificationId) }
    }
}
