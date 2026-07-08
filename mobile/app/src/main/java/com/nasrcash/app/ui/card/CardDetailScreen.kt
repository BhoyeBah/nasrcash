package com.nasrcash.app.ui.card

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.nasrcash.app.core.network.CardPaymentResponse
import com.nasrcash.app.ui.common.ErrorText
import com.nasrcash.app.ui.common.LoadingButton
import com.nasrcash.app.ui.common.UiState
import com.nasrcash.app.ui.common.nasrCashViewModel

@Composable
fun CardDetailScreen(cardId: String) {
    val viewModel = nasrCashViewModel { CardDetailViewModel(it.cardRepository, cardId) }
    val state by viewModel.state.collectAsState()
    val actionError by viewModel.actionError.collectAsState()
    val actionInProgress by viewModel.actionInProgress.collectAsState()
    var showFundDialog by remember { mutableStateOf(false) }

    when (val currentState = state) {
        is UiState.Loading, UiState.Idle -> Box(Modifier.fillMaxSize(), Alignment.Center) { CircularProgressIndicator() }
        is UiState.Error -> ErrorText(currentState.message, Modifier.padding(24.dp))
        is UiState.Success -> {
            val data = currentState.data
            LazyColumn(modifier = Modifier.fillMaxSize().padding(24.dp)) {
                item {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primary),
                    ) {
                        Column(Modifier.padding(20.dp)) {
                            Text(data.card.masked_pan, color = MaterialTheme.colorScheme.onPrimary, style = MaterialTheme.typography.titleLarge)
                            Text(
                                "${data.card.brand.uppercase()} · expire ${data.card.expiry_month}/${data.card.expiry_year}",
                                color = MaterialTheme.colorScheme.onPrimary,
                            )
                            Text(
                                "${data.balance} ${data.card.displayed_currency}",
                                color = MaterialTheme.colorScheme.onPrimary,
                                style = MaterialTheme.typography.headlineSmall,
                                modifier = Modifier.padding(top = 12.dp),
                            )
                            Text(
                                "Statut : ${data.card.status}",
                                color = MaterialTheme.colorScheme.onPrimary,
                            )
                        }
                    }
                }

                item {
                    Row(modifier = Modifier.fillMaxWidth().padding(top = 16.dp)) {
                        Button(onClick = { showFundDialog = true }, enabled = data.card.status == "active") {
                            Text("Recharger")
                        }
                        Spacer(modifier = Modifier.width(8.dp))
                        if (data.card.status == "active") {
                            OutlinedButton(onClick = viewModel::freeze, enabled = !actionInProgress) { Text("Geler") }
                        } else if (data.card.status == "frozen") {
                            OutlinedButton(onClick = viewModel::unfreeze, enabled = !actionInProgress) { Text("Dégeler") }
                        }
                        Spacer(modifier = Modifier.width(8.dp))
                        if (data.card.status != "closed") {
                            OutlinedButton(onClick = viewModel::close, enabled = !actionInProgress) { Text("Fermer") }
                        }
                    }
                }

                actionError?.let { item { ErrorText(it) } }

                item {
                    Text(
                        "Historique des paiements",
                        style = MaterialTheme.typography.titleMedium,
                        modifier = Modifier.padding(top = 24.dp, bottom = 8.dp),
                    )
                }

                if (data.payments.isEmpty()) {
                    item { Text("Aucun paiement pour le moment", color = MaterialTheme.colorScheme.onSurfaceVariant) }
                } else {
                    items(data.payments) { payment -> PaymentRow(payment) }
                }
            }

            if (showFundDialog) {
                FundDialog(
                    isLoading = actionInProgress,
                    onDismiss = { showFundDialog = false },
                    onConfirm = { amount ->
                        viewModel.fund(amount)
                        showFundDialog = false
                    },
                )
            }
        }
    }
}

@Composable
private fun PaymentRow(payment: CardPaymentResponse) {
    Card(modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp)) {
        Column(Modifier.padding(12.dp)) {
            Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                Text(payment.merchant_name, style = MaterialTheme.typography.bodyLarge)
                Text(payment.status, color = if (payment.status == "declined") MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.primary)
            }
            Text("${payment.merchant_amount} ${payment.merchant_currency} · taux ${payment.fx_rate}")
            if (payment.status == "settled") {
                Text("${payment.total_debited} ${payment.local_currency} débités", style = MaterialTheme.typography.bodySmall)
            }
            payment.decline_reason?.let {
                Text("Motif : $it", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.error)
            }
        }
    }
}

@Composable
private fun FundDialog(isLoading: Boolean, onDismiss: () -> Unit, onConfirm: (String) -> Unit) {
    var amount by remember { mutableStateOf("") }
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Recharger la carte") },
        text = {
            OutlinedTextField(
                value = amount,
                onValueChange = { amount = it.filter { c -> c.isDigit() || c == '.' } },
                label = { Text("Montant (depuis le wallet)") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            )
        },
        confirmButton = {
            LoadingButton(text = "Confirmer", isLoading = isLoading, onClick = { onConfirm(amount) })
        },
        dismissButton = { TextButton(onClick = onDismiss) { Text("Annuler") } },
    )
}
