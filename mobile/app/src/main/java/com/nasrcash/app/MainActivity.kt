package com.nasrcash.app

import android.os.Bundle
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.fragment.app.FragmentActivity
import com.nasrcash.app.ui.navigation.NasrCashNavHost
import com.nasrcash.app.ui.theme.NasrCashTheme

/**
 * Extends FragmentActivity (not plain ComponentActivity) because
 * BiometricPrompt requires a Fragment/FragmentActivity host — see
 * core/session/BiometricHelper.kt.
 */
class MainActivity : FragmentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            NasrCashTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    NasrCashNavHost()
                }
            }
        }
    }
}
