package com.nasrcash.app.ui.history

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.nasrcash.app.core.network.LedgerEntryResponse
import com.nasrcash.app.ui.common.ErrorText
import com.nasrcash.app.ui.common.UiState
import com.nasrcash.app.ui.common.nasrCashViewModel

@Composable
fun HistoryScreen(walletId: String) {
    val viewModel = nasrCashViewModel { HistoryViewModel(it.walletRepository, walletId) }
    val state by viewModel.state.collectAsState()

    when (val currentState = state) {
        is UiState.Loading, UiState.Idle -> Box(Modifier.fillMaxSize(), Alignment.Center) { CircularProgressIndicator() }
        is UiState.Error -> ErrorText(currentState.message, Modifier.padding(24.dp))
        is UiState.Success -> {
            if (currentState.data.isEmpty()) {
                Box(Modifier.fillMaxSize(), Alignment.Center) { Text("Aucune transaction") }
            } else {
                LazyColumn(modifier = Modifier.fillMaxSize().padding(16.dp)) {
                    items(currentState.data) { entry -> TransactionRow(entry) }
                }
            }
        }
    }
}

@Composable
private fun TransactionRow(entry: LedgerEntryResponse) {
    val isCredit = entry.direction == "credit"
    Card(modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Column {
                Text(entry.description ?: entry.direction, style = MaterialTheme.typography.bodyLarge)
                Text(entry.created_at, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
            Text(
                "${if (isCredit) "+" else "-"}${entry.amount} ${entry.currency}",
                color = if (isCredit) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error,
            )
        }
    }
}
