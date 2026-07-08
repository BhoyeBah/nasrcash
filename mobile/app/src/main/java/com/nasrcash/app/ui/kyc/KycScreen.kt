package com.nasrcash.app.ui.kyc

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.nasrcash.app.ui.common.ErrorText
import com.nasrcash.app.ui.common.LoadingButton
import com.nasrcash.app.ui.common.UiState
import com.nasrcash.app.ui.common.nasrCashViewModel

private val DOCUMENT_LABELS = mapOf(
    "national_id" to "Carte nationale d'identité",
    "selfie" to "Selfie",
    "proof_of_address" to "Justificatif de domicile",
)

private fun requiredDocsForLevel(level: Int): List<String> =
    if (level >= 2) listOf("national_id", "selfie", "proof_of_address") else listOf("national_id", "selfie")

@Composable
fun KycScreen(onDone: () -> Unit) {
    val viewModel = nasrCashViewModel { KycViewModel(it.kycRepository) }
    val state by viewModel.state.collectAsState()
    val actionError by viewModel.actionError.collectAsState()
    val uploadingType by viewModel.uploadingType.collectAsState()

    val context = LocalContext.current
    var pendingDocType by remember { mutableStateOf<String?>(null) }

    val pickDocument = rememberLauncherForActivityResult(ActivityResultContracts.GetContent()) { uri ->
        val docType = pendingDocType ?: return@rememberLauncherForActivityResult
        if (uri != null) {
            val bytes = context.contentResolver.openInputStream(uri)?.use { it.readBytes() }
            if (bytes != null) {
                viewModel.uploadDocument(docType, "$docType.jpg", "image/jpeg", bytes)
            }
        }
        pendingDocType = null
    }

    Column(modifier = Modifier.fillMaxSize().padding(24.dp)) {
        Text("Vérification d'identité (KYC)", style = MaterialTheme.typography.headlineSmall)

        when (val currentState = state) {
            is UiState.Loading, UiState.Idle -> CircularProgressIndicator(modifier = Modifier.padding(top = 24.dp))
            is UiState.Error -> ErrorText(currentState.message)
            is UiState.Success -> {
                val status = currentState.data
                val profile = status.profile

                when {
                    profile == null || profile.status in listOf("rejected") -> {
                        if (profile?.status == "rejected") {
                            Card(modifier = Modifier.fillMaxWidth().padding(top = 16.dp)) {
                                Column(Modifier.padding(16.dp)) {
                                    Text("Dossier précédent rejeté")
                                    Text(profile.rejection_reason ?: "", style = MaterialTheme.typography.bodySmall)
                                }
                            }
                        }
                        Text(
                            "Niveau KYC actuel : ${status.current_kyc_level}. Une carte virtuelle nécessite le niveau 2.",
                            modifier = Modifier.padding(top = 16.dp),
                        )
                        LoadingButton(
                            text = "Commencer la vérification",
                            isLoading = false,
                            onClick = { viewModel.start() },
                            modifier = Modifier.fillMaxWidth().padding(top = 16.dp),
                        )
                    }

                    profile.status in listOf("submitted", "under_review") -> {
                        Text(
                            "Votre dossier est en cours de revue.",
                            modifier = Modifier.padding(top = 24.dp),
                        )
                    }

                    profile.status == "approved" -> {
                        Row(modifier = Modifier.padding(top = 24.dp)) {
                            Icon(Icons.Filled.CheckCircle, contentDescription = null, tint = MaterialTheme.colorScheme.primary)
                            Text(
                                "KYC niveau ${profile.level_requested} approuvé",
                                modifier = Modifier.padding(start = 8.dp),
                            )
                        }
                        LoadingButton(
                            text = "Retour",
                            isLoading = false,
                            onClick = onDone,
                            modifier = Modifier.fillMaxWidth().padding(top = 16.dp),
                        )
                    }

                    else -> {
                        // draft or requires_more_info: documents can still be added/submitted
                        val uploadedTypes = status.documents.map { it.document_type }.toSet()
                        val required = requiredDocsForLevel(profile.level_requested)

                        Column(modifier = Modifier.padding(top = 16.dp)) {
                            required.forEach { docType ->
                                val isUploaded = docType in uploadedTypes
                                Row(
                                    modifier = Modifier.fillMaxWidth().padding(vertical = 6.dp),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                ) {
                                    Text(DOCUMENT_LABELS[docType] ?: docType)
                                    if (isUploaded) {
                                        Icon(Icons.Filled.CheckCircle, contentDescription = "Envoyé", tint = MaterialTheme.colorScheme.primary)
                                    } else if (uploadingType == docType) {
                                        CircularProgressIndicator(modifier = Modifier.padding(0.dp))
                                    } else {
                                        OutlinedButton(onClick = {
                                            pendingDocType = docType
                                            pickDocument.launch("image/*")
                                        }) { Text("Ajouter") }
                                    }
                                }
                            }

                            actionError?.let { ErrorText(it) }

                            LoadingButton(
                                text = "Soumettre mon dossier",
                                isLoading = false,
                                enabled = required.all { it in uploadedTypes },
                                onClick = { viewModel.submit() },
                                modifier = Modifier.fillMaxWidth().padding(top = 16.dp),
                            )
                        }
                    }
                }
            }
        }
    }
}
