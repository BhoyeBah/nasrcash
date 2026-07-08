package com.nasrcash.app.ui.auth

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.fragment.app.FragmentActivity
import com.nasrcash.app.core.session.BiometricHelper
import com.nasrcash.app.ui.common.ErrorText
import com.nasrcash.app.ui.common.LoadingButton

/**
 * Shown at cold start when a session already exists — re-proves it's the
 * same person via biometrics before handing back the wallet/card UI, rather
 * than trusting an app-in-background reopen unconditionally.
 */
@Composable
fun AppLockScreen(onUnlocked: () -> Unit, onUseSessionExpired: () -> Unit) {
    val activity = LocalContext.current as FragmentActivity
    var error by remember { mutableStateOf<String?>(null) }
    val biometricAvailable = remember { BiometricHelper.isAvailable(activity) }

    LaunchedEffect(Unit) {
        if (biometricAvailable) {
            BiometricHelper.authenticate(
                activity,
                onSuccess = onUnlocked,
                onFailure = { error = it },
            )
        }
    }

    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.Center,
    ) {
        Text("NasrCash", style = MaterialTheme.typography.headlineMedium, color = MaterialTheme.colorScheme.primary)
        Text(
            if (biometricAvailable) "Déverrouillage biométrique en cours..." else "Biométrie indisponible sur cet appareil",
        )
        error?.let { ErrorText(it) }

        if (biometricAvailable) {
            LoadingButton(
                text = "Réessayer",
                isLoading = false,
                onClick = {
                    error = null
                    BiometricHelper.authenticate(activity, onUnlocked) { error = it }
                },
                modifier = Modifier.fillMaxWidth().padding(top = 16.dp),
            )
        }

        TextButton(onClick = onUseSessionExpired, modifier = Modifier.padding(top = 8.dp)) {
            Text("Se reconnecter avec mon PIN")
        }
    }
}
