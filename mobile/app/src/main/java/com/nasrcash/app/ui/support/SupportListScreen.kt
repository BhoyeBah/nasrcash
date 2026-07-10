package com.nasrcash.app.ui.support

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.nasrcash.app.core.network.TicketResponse
import com.nasrcash.app.ui.common.ErrorText
import com.nasrcash.app.ui.common.LoadingButton
import com.nasrcash.app.ui.common.UiState
import com.nasrcash.app.ui.common.nasrCashViewModel

private val CATEGORIES = listOf("general", "kyc", "topup", "withdrawal", "card", "payment")

@Composable
fun SupportListScreen(onOpenTicket: (String) -> Unit) {
    val viewModel = nasrCashViewModel { SupportListViewModel(it.supportRepository) }
    val state by viewModel.state.collectAsState()
    val actionError by viewModel.actionError.collectAsState()
    val creating by viewModel.creating.collectAsState()
    var showCreateDialog by remember { mutableStateOf(false) }

    Scaffold(
        topBar = { TopAppBar(title = { Text("Support") }) },
        floatingActionButton = {
            FloatingActionButton(onClick = { showCreateDialog = true }) {
                Icon(Icons.Filled.Add, contentDescription = "Nouveau ticket")
            }
        },
    ) { padding ->
        when (val currentState = state) {
            is UiState.Loading, UiState.Idle -> Box(
                Modifier.fillMaxSize().padding(padding),
                contentAlignment = Alignment.Center,
            ) { CircularProgressIndicator() }

            is UiState.Error -> Box(Modifier.fillMaxSize().padding(padding)) { ErrorText(currentState.message) }

            is UiState.Success -> {
                if (currentState.data.isEmpty()) {
                    Box(Modifier.fillMaxSize().padding(padding), Alignment.Center) {
                        Text("Aucun ticket. Appuyez sur + pour en créer un.")
                    }
                } else {
                    LazyColumn(modifier = Modifier.fillMaxSize().padding(padding).padding(16.dp)) {
                        items(currentState.data) { ticket ->
                            TicketRow(ticket, onClick = { onOpenTicket(ticket.id) })
                        }
                    }
                }
            }
        }
    }

    if (showCreateDialog) {
        CreateTicketDialog(
            isLoading = creating,
            error = actionError,
            onDismiss = { showCreateDialog = false; viewModel.clearActionError() },
            onConfirm = { subject, category, message ->
                viewModel.createTicket(subject, category, message) { ticketId ->
                    showCreateDialog = false
                    onOpenTicket(ticketId)
                }
            },
        )
    }
}

@Composable
private fun TicketRow(ticket: TicketResponse, onClick: () -> Unit) {
    Card(modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp), onClick = onClick) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Column {
                Text(ticket.subject, style = MaterialTheme.typography.bodyLarge)
                Text(
                    ticket.category,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            Text(ticket.status, style = MaterialTheme.typography.bodySmall)
        }
    }
}

@Composable
private fun CreateTicketDialog(
    isLoading: Boolean,
    error: String?,
    onDismiss: () -> Unit,
    onConfirm: (subject: String, category: String, message: String) -> Unit,
) {
    var subject by remember { mutableStateOf("") }
    var category by remember { mutableStateOf(CATEGORIES.first()) }
    var message by remember { mutableStateOf("") }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Nouveau ticket") },
        text = {
            Column {
                OutlinedTextField(
                    value = subject,
                    onValueChange = { subject = it },
                    label = { Text("Sujet") },
                    modifier = Modifier.fillMaxWidth(),
                )
                Text(
                    "Catégorie",
                    style = MaterialTheme.typography.labelMedium,
                    modifier = Modifier.padding(top = 8.dp),
                )
                Row(
                    modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                ) {
                    CATEGORIES.forEach { option ->
                        FilterChip(
                            selected = category == option,
                            onClick = { category = option },
                            label = { Text(option) },
                        )
                    }
                }
                OutlinedTextField(
                    value = message,
                    onValueChange = { message = it },
                    label = { Text("Message") },
                    minLines = 3,
                    modifier = Modifier.fillMaxWidth().padding(top = 8.dp),
                )
                error?.let { ErrorText(it) }
            }
        },
        confirmButton = {
            LoadingButton(
                text = "Créer",
                isLoading = isLoading,
                onClick = { onConfirm(subject, category, message) },
            )
        },
        dismissButton = { TextButton(onClick = onDismiss) { Text("Annuler") } },
    )
}
