package com.nasrcash.app.ui.topup

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Card
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.nasrcash.app.ui.common.ErrorText
import com.nasrcash.app.ui.common.LoadingButton
import com.nasrcash.app.ui.common.nasrCashViewModel

@Composable
fun TopupScreen(walletId: String, onDone: () -> Unit) {
    val viewModel = nasrCashViewModel { TopupViewModel(it.walletRepository, walletId) }
    val state by viewModel.state.collectAsState()

    var amount by remember { mutableStateOf("") }
    var provider by remember { mutableStateOf(TOPUP_PROVIDERS.first().first) }

    Column(modifier = Modifier.fillMaxSize().padding(24.dp)) {
        Text("Recharger mon wallet", style = MaterialTheme.typography.headlineSmall)

        when (val currentState = state) {
            is TopupScreenState.Form, is TopupScreenState.Submitting, is TopupScreenState.Error -> {
                OutlinedTextField(
                    value = amount,
                    onValueChange = { amount = it.filter { c -> c.isDigit() || c == '.' } },
                    label = { Text("Montant (GNF)") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.fillMaxWidth().padding(top = 16.dp),
                )

                Text("Moyen de recharge", modifier = Modifier.padding(top = 16.dp, bottom = 8.dp))
                Column {
                    TOPUP_PROVIDERS.forEach { (value, label) ->
                        FilterChip(
                            selected = provider == value,
                            onClick = { provider = value },
                            label = { Text(label) },
                            modifier = Modifier.padding(bottom = 4.dp),
                        )
                    }
                }

                if (currentState is TopupScreenState.Error) ErrorText(currentState.message)

                LoadingButton(
                    text = "Recharger",
                    isLoading = currentState is TopupScreenState.Submitting,
                    onClick = { viewModel.initiate(amount, provider) },
                    modifier = Modifier.fillMaxWidth().padding(top = 24.dp),
                )
            }

            is TopupScreenState.PendingConfirmation, is TopupScreenState.Confirming -> {
                val topup = when (currentState) {
                    is TopupScreenState.PendingConfirmation -> currentState.topup
                    is TopupScreenState.Confirming -> null
                    else -> null
                }
                Card(modifier = Modifier.fillMaxWidth().padding(top = 24.dp)) {
                    Column(Modifier.padding(16.dp)) {
                        Text("Recharge en attente de confirmation")
                        if (topup != null) {
                            Text("Montant : ${topup.amount} ${topup.currency_code}")
                            Text("Frais : ${topup.fee_amount} ${topup.currency_code}")
                            Text("Net crédité : ${topup.net_amount} ${topup.currency_code}")
                        }
                        Text(
                            "En sandbox, aucun vrai SMS Mobile Money n'est envoyé — confirmez manuellement ci-dessous.",
                            style = MaterialTheme.typography.bodySmall,
                        )
                    }
                }
                LoadingButton(
                    text = "Confirmer la réception (sandbox)",
                    isLoading = currentState is TopupScreenState.Confirming,
                    onClick = {
                        val id = (currentState as? TopupScreenState.PendingConfirmation)?.topup?.id
                        if (id != null) viewModel.confirmSandboxSuccess(id)
                    },
                    modifier = Modifier.fillMaxWidth().padding(top = 16.dp),
                )
            }

            is TopupScreenState.Completed -> {
                Column(
                    modifier = Modifier.fillMaxSize(),
                    verticalArrangement = Arrangement.Center,
                ) {
                    Text("Recharge réussie ✅", style = MaterialTheme.typography.headlineSmall)
                    Text("${currentState.topup.net_amount} ${currentState.topup.currency_code} crédités sur votre wallet.")
                    LoadingButton(
                        text = "Retour",
                        isLoading = false,
                        onClick = onDone,
                        modifier = Modifier.fillMaxWidth().padding(top = 16.dp),
                    )
                }
            }
        }
    }
}
