package com.nasrcash.app.ui.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.nasrcash.app.NasrCashApplication
import com.nasrcash.app.core.network.ApiResult
import com.nasrcash.app.ui.auth.AppLockScreen
import com.nasrcash.app.ui.auth.LoginScreen
import com.nasrcash.app.ui.card.CardDetailScreen
import com.nasrcash.app.ui.common.ErrorText
import com.nasrcash.app.ui.history.HistoryScreen
import com.nasrcash.app.ui.home.HomeScreen
import com.nasrcash.app.ui.kyc.KycScreen
import com.nasrcash.app.ui.notifications.NotificationsScreen
import com.nasrcash.app.ui.onboarding.OtpScreen
import com.nasrcash.app.ui.onboarding.RegisterScreen
import com.nasrcash.app.ui.topup.TopupScreen
import com.nasrcash.app.ui.withdrawal.WithdrawalScreen

@Composable
fun NasrCashNavHost(navController: NavHostController = rememberNavController()) {
    val container = (LocalContext.current.applicationContext as NasrCashApplication).container
    val isLoggedIn by container.isLoggedIn.collectAsState()
    val startDestination = if (isLoggedIn) "applock" else Routes.LOGIN

    NavHost(navController = navController, startDestination = startDestination) {
        composable("applock") {
            AppLockScreen(
                onUnlocked = {
                    navController.navigate(Routes.HOME) { popUpTo("applock") { inclusive = true } }
                },
                onUseSessionExpired = {
                    navController.navigate(Routes.LOGIN) { popUpTo("applock") { inclusive = true } }
                },
            )
        }

        composable(Routes.LOGIN) {
            LoginScreen(
                onLoggedIn = { navController.navigate(Routes.HOME) { popUpTo(Routes.LOGIN) { inclusive = true } } },
                onGoToRegister = { navController.navigate(Routes.REGISTER) },
            )
        }

        composable(Routes.REGISTER) {
            RegisterScreen(
                onRegistered = { phone -> navController.navigate(Routes.otp(phone)) },
                onGoToLogin = { navController.popBackStack() },
            )
        }

        composable(Routes.OTP) { backStackEntry ->
            val phone = backStackEntry.arguments?.getString("phone").orEmpty()
            OtpScreen(
                phone = phone,
                onVerified = { navController.navigate(Routes.HOME) { popUpTo(Routes.LOGIN) { inclusive = true } } },
            )
        }

        composable(Routes.HOME) {
            HomeScreen(
                onOpenTopup = { navController.navigate(Routes.TOPUP) },
                onOpenWithdrawal = { navController.navigate(Routes.WITHDRAWAL) },
                onOpenKyc = { navController.navigate(Routes.KYC) },
                onOpenCard = { cardId -> navController.navigate(Routes.cardDetail(cardId)) },
                onOpenHistory = { walletId -> navController.navigate(Routes.history(walletId)) },
                onOpenNotifications = { navController.navigate(Routes.NOTIFICATIONS) },
            )
        }

        composable(Routes.TOPUP) {
            WalletScopedRoute { walletId -> TopupScreen(walletId = walletId, onDone = { navController.popBackStack() }) }
        }

        composable(Routes.WITHDRAWAL) {
            WalletScopedRoute { walletId ->
                WithdrawalScreen(walletId = walletId, onDone = { navController.popBackStack() })
            }
        }

        composable(Routes.KYC) {
            KycScreen(onDone = { navController.popBackStack() })
        }

        composable(Routes.CARD_DETAIL) { backStackEntry ->
            val cardId = backStackEntry.arguments?.getString("cardId").orEmpty()
            CardDetailScreen(cardId = cardId)
        }

        composable(Routes.HISTORY) { backStackEntry ->
            val walletId = backStackEntry.arguments?.getString("walletId").orEmpty()
            HistoryScreen(walletId = walletId)
        }

        composable(Routes.NOTIFICATIONS) {
            NotificationsScreen()
        }
    }
}

/** Resolves the current user's wallet id once, then hands off to [content]. */
@Composable
private fun WalletScopedRoute(content: @Composable (walletId: String) -> Unit) {
    val container = (LocalContext.current.applicationContext as NasrCashApplication).container
    var walletId by remember { mutableStateOf<String?>(null) }
    var error by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(Unit) {
        when (val result = container.walletRepository.getPrimaryWallet()) {
            is ApiResult.Success -> walletId = result.data.id
            is ApiResult.Error -> error = result.message
        }
    }

    when {
        error != null -> ErrorText(error!!)
        walletId != null -> content(walletId!!)
        else -> CircularProgressIndicator(modifier = Modifier.padding(24.dp))
    }
}
