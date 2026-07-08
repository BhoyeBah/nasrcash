package com.nasrcash.app.ui.notifications

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.nasrcash.app.core.network.NotificationResponse
import com.nasrcash.app.ui.common.nasrCashViewModel

@Composable
fun NotificationsScreen() {
    val viewModel = nasrCashViewModel { NotificationsViewModel(it.notificationRepository) }
    val notifications by viewModel.notifications.collectAsState()

    if (notifications.isEmpty()) {
        Box(Modifier.fillMaxSize(), Alignment.Center) { Text("Aucune notification") }
        return
    }

    LazyColumn(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        items(notifications) { notification ->
            NotificationRow(notification, onClick = { viewModel.markRead(notification.id) })
        }
    }
}

@Composable
private fun NotificationRow(notification: NotificationResponse, onClick: () -> Unit) {
    val isUnread = notification.read_at == null
    Card(
        modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (isUnread) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface,
        ),
        onClick = onClick,
    ) {
        Column(Modifier.padding(16.dp)) {
            Text(notification.title, style = MaterialTheme.typography.bodyLarge)
            Text(notification.body, style = MaterialTheme.typography.bodyMedium)
            Text(notification.created_at, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}
