package com.nasrcash.app.ui.support

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.nasrcash.app.core.network.TicketMessageResponse
import com.nasrcash.app.ui.common.ErrorText
import com.nasrcash.app.ui.common.LoadingButton
import com.nasrcash.app.ui.common.UiState
import com.nasrcash.app.ui.common.nasrCashViewModel

@Composable
fun SupportDetailScreen(ticketId: String) {
    val viewModel = nasrCashViewModel { SupportDetailViewModel(it.supportRepository, ticketId) }
    val state by viewModel.state.collectAsState()
    val actionError by viewModel.actionError.collectAsState()
    val sending by viewModel.sending.collectAsState()
    var replyText by remember { mutableStateOf("") }

    when (val currentState = state) {
        is UiState.Loading, UiState.Idle -> Box(Modifier.fillMaxSize(), Alignment.Center) { CircularProgressIndicator() }
        is UiState.Error -> ErrorText(currentState.message, Modifier.padding(24.dp))
        is UiState.Success -> {
            val data = currentState.data
            val isClosed = data.ticket.status == "resolved" || data.ticket.status == "closed"

            Scaffold(
                topBar = { TopAppBar(title = { Text(data.ticket.subject) }) },
            ) { padding ->
                Column(modifier = Modifier.fillMaxSize().padding(padding)) {
                    LazyColumn(modifier = Modifier.weight(1f).fillMaxWidth().padding(16.dp)) {
                        items(data.messages) { message -> MessageBubble(message) }
                    }

                    if (isClosed) {
                        Text(
                            "Ce ticket est ${data.ticket.status} — vous ne pouvez plus répondre.",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.padding(16.dp),
                        )
                    } else {
                        Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
                            OutlinedTextField(
                                value = replyText,
                                onValueChange = { replyText = it },
                                label = { Text("Votre message") },
                                modifier = Modifier.fillMaxWidth(),
                            )
                            actionError?.let { ErrorText(it) }
                            LoadingButton(
                                text = "Envoyer",
                                isLoading = sending,
                                onClick = {
                                    viewModel.sendReply(replyText)
                                    replyText = ""
                                },
                                modifier = Modifier.padding(top = 8.dp),
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun MessageBubble(message: TicketMessageResponse) {
    val isAdmin = message.sender_type == "admin"
    Row(modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp)) {
        Column(
            modifier = Modifier
                .background(
                    if (isAdmin) MaterialTheme.colorScheme.secondaryContainer else MaterialTheme.colorScheme.surfaceVariant,
                    RoundedCornerShape(8.dp),
                )
                .padding(12.dp),
        ) {
            Text(
                if (isAdmin) "Support" else "Vous",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(message.body, style = MaterialTheme.typography.bodyMedium)
        }
    }
}
