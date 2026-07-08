package com.nasrcash.app.ui.common

import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewmodel.compose.viewModel
import com.nasrcash.app.NasrCashApplication
import com.nasrcash.app.core.di.AppContainer

/** Generic factory so each ViewModel can take [AppContainer] dependencies in its constructor. */
class GenericViewModelFactory<T : ViewModel>(
    private val container: AppContainer,
    private val creator: (AppContainer) -> T,
) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <U : ViewModel> create(modelClass: Class<U>): U = creator(container) as U
}

/** Builds a screen's ViewModel from the app-wide [AppContainer], e.g.:
 * `val viewModel = nasrCashViewModel { container -> HomeViewModel(container.walletRepository) }` */
@Composable
inline fun <reified T : ViewModel> nasrCashViewModel(noinline creator: (AppContainer) -> T): T {
    val context = LocalContext.current
    val container = (context.applicationContext as NasrCashApplication).container
    return viewModel(factory = GenericViewModelFactory(container, creator))
}
