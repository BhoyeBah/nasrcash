package com.nasrcash.app.ui.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material3.Badge
import androidx.compose.material3.BadgedBox
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.nasrcash.app.core.network.CardResponse
import com.nasrcash.app.ui.common.ErrorText
import com.nasrcash.app.ui.common.UiState
import com.nasrcash.app.ui.common.nasrCashViewModel

@Composable
fun HomeScreen(
    onOpenTopup: () -> Unit,
    onOpenWithdrawal: () -> Unit,
    onOpenKyc: () -> Unit,
    onOpenCard: (String) -> Unit,
    onOpenHistory: (String) -> Unit,
    onOpenNotifications: () -> Unit,
) {
    val viewModel = nasrCashViewModel {
        HomeViewModel(it.walletRepository, it.cardRepository, it.notificationRepository)
    }
    val state by viewModel.state.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("NasrCash") },
                actions = {
                    val unread = (state as? UiState.Success)?.data?.unreadNotifications ?: 0
                    IconButton(onClick = onOpenNotifications) {
                        BadgedBox(badge = { if (unread > 0) Badge { Text("$unread") } }) {
                            Icon(Icons.Filled.Notifications, contentDescription = "Notifications")
                        }
                    }
                },
            )
        },
    ) { padding ->
        when (val currentState = state) {
            is UiState.Loading, UiState.Idle -> Box(
                Modifier.fillMaxSize().padding(padding),
                contentAlignment = Alignment.Center,
            ) { CircularProgressIndicator() }

            is UiState.Error -> Box(Modifier.fillMaxSize().padding(padding)) { ErrorText(currentState.message) }

            is UiState.Success -> HomeContent(
                data = currentState.data,
                modifier = Modifier.padding(padding),
                onOpenTopup = onOpenTopup,
                onOpenWithdrawal = onOpenWithdrawal,
                onOpenKyc = onOpenKyc,
                onOpenCard = onOpenCard,
                onOpenHistory = onOpenHistory,
            )
        }
    }
}

@Composable
private fun HomeContent(
    data: HomeData,
    modifier: Modifier = Modifier,
    onOpenTopup: () -> Unit,
    onOpenWithdrawal: () -> Unit,
    onOpenKyc: () -> Unit,
    onOpenCard: (String) -> Unit,
    onOpenHistory: (String) -> Unit,
) {
    LazyColumn(modifier = modifier.fillMaxSize().padding(16.dp)) {
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primary),
            ) {
                Column(Modifier.padding(20.dp)) {
                    Text(
                        "Solde wallet",
                        color = MaterialTheme.colorScheme.onPrimary,
                        style = MaterialTheme.typography.labelLarge,
                    )
                    Text(
                        "${data.walletBalance} ${data.wallet.currency_code}",
                        color = MaterialTheme.colorScheme.onPrimary,
                        style = MaterialTheme.typography.headlineMedium,
                    )
                    Row(modifier = Modifier.padding(top = 12.dp)) {
                        Button(onClick = onOpenTopup) { Text("Recharger") }
                        OutlinedButton(
                            onClick = onOpenWithdrawal,
                            modifier = Modifier.padding(start = 8.dp),
                        ) { Text("Retirer") }
                        OutlinedButton(
                            onClick = { onOpenHistory(data.wallet.id) },
                            modifier = Modifier.padding(start = 8.dp),
                        ) { Text("Historique") }
                    }
                }
            }
        }

        item {
            Text(
                "Mes cartes virtuelles",
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(top = 24.dp, bottom = 8.dp),
            )
        }

        if (data.cards.isEmpty()) {
            item {
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(Modifier.padding(16.dp)) {
                        Text("Vous n'avez pas encore de carte virtuelle.")
                        Text(
                            "Un niveau KYC 2 est requis pour en créer une.",
                            style = MaterialTheme.typography.bodySmall,
                        )
                        Button(onClick = onOpenKyc, modifier = Modifier.padding(top = 12.dp)) {
                            Text("Compléter mon KYC")
                        }
                    }
                }
            }
        } else {
            items(data.cards) { card -> CardRow(card, onClick = { onOpenCard(card.id) }) }
        }
    }
}

@Composable
private fun CardRow(card: CardResponse, onClick: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
        onClick = onClick,
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Column {
                Text(card.masked_pan, style = MaterialTheme.typography.bodyLarge)
                Text(
                    "${card.brand.uppercase()} · ${card.status}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}
