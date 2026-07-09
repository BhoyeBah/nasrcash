package com.nasrcash.app.ui.withdrawal

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
fun WithdrawalScreen(walletId: String, onDone: () -> Unit) {
    val viewModel = nasrCashViewModel { WithdrawalViewModel(it.walletRepository, walletId) }
    val state by viewModel.state.collectAsState()

    var amount by remember { mutableStateOf("") }
    var provider by remember { mutableStateOf(WITHDRAWAL_PROVIDERS.first().first) }

    Column(modifier = Modifier.fillMaxSize().padding(24.dp)) {
        Text("Retirer vers Mobile Money", style = MaterialTheme.typography.headlineSmall)

        when (val currentState = state) {
            is WithdrawalScreenState.Form, is WithdrawalScreenState.Submitting, is WithdrawalScreenState.Error -> {
                OutlinedTextField(
                    value = amount,
                    onValueChange = { amount = it.filter { c -> c.isDigit() || c == '.' } },
                    label = { Text("Montant (GNF)") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.fillMaxWidth().padding(top = 16.dp),
                )

                Text("Moyen de retrait", modifier = Modifier.padding(top = 16.dp, bottom = 8.dp))
                Column {
                    WITHDRAWAL_PROVIDERS.forEach { (value, label) ->
                        FilterChip(
                            selected = provider == value,
                            onClick = { provider = value },
                            label = { Text(label) },
                            modifier = Modifier.padding(bottom = 4.dp),
                        )
                    }
                }

                if (currentState is WithdrawalScreenState.Error) ErrorText(currentState.message)

                LoadingButton(
                    text = "Retirer",
                    isLoading = currentState is WithdrawalScreenState.Submitting,
                    onClick = { viewModel.initiate(amount, provider) },
                    modifier = Modifier.fillMaxWidth().padding(top = 24.dp),
                )
            }

            is WithdrawalScreenState.PendingConfirmation, is WithdrawalScreenState.Confirming -> {
                val withdrawal = (currentState as? WithdrawalScreenState.PendingConfirmation)?.withdrawal
                Card(modifier = Modifier.fillMaxWidth().padding(top = 24.dp)) {
                    Column(Modifier.padding(16.dp)) {
                        Text("Retrait en attente de confirmation")
                        if (withdrawal != null) {
                            Text("Montant débité : ${withdrawal.amount} ${withdrawal.currency_code}")
                            Text("Frais : ${withdrawal.fee_amount} ${withdrawal.currency_code}")
                            Text("Net envoyé : ${withdrawal.net_amount} ${withdrawal.currency_code}")
                        }
                        Text(
                            "En sandbox, aucun vrai virement Mobile Money n'est envoyé — confirmez manuellement ci-dessous.",
                            style = MaterialTheme.typography.bodySmall,
                        )
                    }
                }
                LoadingButton(
                    text = "Confirmer l'envoi (sandbox)",
                    isLoading = currentState is WithdrawalScreenState.Confirming,
                    onClick = {
                        val id = (currentState as? WithdrawalScreenState.PendingConfirmation)?.withdrawal?.id
                        if (id != null) viewModel.confirmSandboxSuccess(id)
                    },
                    modifier = Modifier.fillMaxWidth().padding(top = 16.dp),
                )
            }

            is WithdrawalScreenState.Completed -> {
                Column(
                    modifier = Modifier.fillMaxSize(),
                    verticalArrangement = Arrangement.Center,
                ) {
                    Text("Retrait envoyé ✅", style = MaterialTheme.typography.headlineSmall)
                    Text(
                        "${currentState.withdrawal.net_amount} ${currentState.withdrawal.currency_code} " +
                            "envoyés vers votre Mobile Money.",
                    )
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
