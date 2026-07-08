package com.nasrcash.app.ui.onboarding

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.nasrcash.app.ui.common.ErrorText
import com.nasrcash.app.ui.common.LoadingButton
import com.nasrcash.app.ui.common.UiState
import com.nasrcash.app.ui.common.nasrCashViewModel

@Composable
fun RegisterScreen(onRegistered: (phone: String) -> Unit, onGoToLogin: () -> Unit) {
    val viewModel = nasrCashViewModel { RegisterViewModel(it.authRepository) }
    val state by viewModel.state.collectAsState()

    var phone by remember { mutableStateOf("+224") }
    var pin by remember { mutableStateOf("") }

    LaunchedEffect(state) {
        if (state is UiState.Success) onRegistered(phone)
    }

    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.Center,
    ) {
        Text("NasrCash", style = MaterialTheme.typography.headlineMedium, color = MaterialTheme.colorScheme.primary)
        Text("Rechargez en GNF. Payez partout dans le monde.", style = MaterialTheme.typography.bodyMedium)

        Column(modifier = Modifier.padding(top = 32.dp)) {
            OutlinedTextField(
                value = phone,
                onValueChange = { phone = it },
                label = { Text("Téléphone") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = pin,
                onValueChange = { if (it.length <= 6) pin = it.filter(Char::isDigit) },
                label = { Text("Code PIN (4 à 6 chiffres)") },
                visualTransformation = PasswordVisualTransformation(),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.NumberPassword),
                modifier = Modifier.fillMaxWidth().padding(top = 8.dp),
            )

            val currentState = state
            if (currentState is UiState.Error) {
                ErrorText(currentState.message)
            }

            LoadingButton(
                text = "Créer mon compte",
                isLoading = state is UiState.Loading,
                onClick = { viewModel.register(phone, "GN", pin) },
                modifier = Modifier.fillMaxWidth().padding(top = 16.dp),
            )

            Text(
                "Déjà un compte ? Se connecter",
                color = MaterialTheme.colorScheme.primary,
                modifier = Modifier.padding(top = 16.dp).clickable(onClick = onGoToLogin),
            )
        }
    }
}
