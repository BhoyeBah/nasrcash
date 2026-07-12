package com.nasrcash.app.ui.home

import com.nasrcash.app.MainDispatcherRule
import com.nasrcash.app.core.network.CardResponse
import com.nasrcash.app.core.network.FakeApiService
import com.nasrcash.app.core.network.KycStatusResponse
import com.nasrcash.app.core.network.UnreadCountResponse
import com.nasrcash.app.core.network.WalletBalanceResponse
import com.nasrcash.app.core.network.WalletResponse
import com.nasrcash.app.data.local.FakeNotificationDao
import com.nasrcash.app.data.repository.CardRepository
import com.nasrcash.app.data.repository.KycRepository
import com.nasrcash.app.data.repository.NotificationRepository
import com.nasrcash.app.data.repository.WalletRepository
import com.nasrcash.app.ui.common.UiState
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test

class HomeViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val wallet = WalletResponse(id = "wallet-1", country_code = "GN", currency_code = "GNF", status = "active")

    private fun card(id: String, status: String = "active") = CardResponse(
        id = id, masked_pan = "4242 **** **** 0000", last4 = "0000", brand = "visa",
        displayed_currency = "GNF", status = status, nickname = null, expiry_month = 1, expiry_year = 2030,
    )

    private fun buildViewModel(
        fakeApi: FakeApiService,
    ): HomeViewModel {
        val notificationRepository = NotificationRepository(fakeApi, FakeNotificationDao())
        return HomeViewModel(
            WalletRepository(fakeApi), CardRepository(fakeApi), notificationRepository, KycRepository(fakeApi),
        )
    }

    @Test
    fun `load aggregates wallet, cards, notifications and kyc level`() = runTest {
        val fakeApi = FakeApiService(
            listWalletsResult = { listOf(wallet) },
            getWalletBalanceResult = { WalletBalanceResponse("wallet-1", "GNF", "125000.00") },
            listCardsResult = { listOf(card("card-1")) },
            getUnreadNotificationCountResult = { UnreadCountResponse(3) },
            getKycStatusResult = { KycStatusResponse(profile = null, documents = emptyList(), current_kyc_level = 2) },
        )

        val viewModel = buildViewModel(fakeApi)

        val state = viewModel.state.value
        assertTrue(state is UiState.Success)
        val data = (state as UiState.Success).data
        assertEquals("125000.00", data.walletBalance)
        assertEquals(1, data.cards.size)
        assertEquals(3, data.unreadNotifications)
        assertEquals(2, data.currentKycLevel)
    }

    @Test
    fun `load surfaces an error when the wallet lookup fails`() = runTest {
        val fakeApi = FakeApiService(listWalletsResult = { throw RuntimeException("Aucun wallet trouvé") })

        val viewModel = buildViewModel(fakeApi)

        val state = viewModel.state.value
        assertTrue(state is UiState.Error)
        assertEquals("Aucun wallet trouvé", (state as UiState.Error).message)
    }

    @Test
    fun `issueCard success refreshes the card list`() = runTest {
        var cardsOnServer = listOf<CardResponse>()
        val fakeApi = FakeApiService(
            listWalletsResult = { listOf(wallet) },
            getWalletBalanceResult = { WalletBalanceResponse("wallet-1", "GNF", "0.00") },
            listCardsResult = { cardsOnServer },
            getUnreadNotificationCountResult = { UnreadCountResponse(0) },
            getKycStatusResult = { KycStatusResponse(null, emptyList(), 2) },
            issueCardResult = {
                val newCard = card("card-new")
                cardsOnServer = cardsOnServer + newCard
                newCard
            },
        )
        val viewModel = buildViewModel(fakeApi)
        assertEquals(0, (viewModel.state.value as UiState.Success).data.cards.size)

        viewModel.issueCard()

        val data = (viewModel.state.value as UiState.Success).data
        assertEquals(1, data.cards.size)
        assertEquals(null, viewModel.actionError.value)
    }

    @Test
    fun `issueCard surfaces a limit_exceeded style error without changing the card list`() = runTest {
        val fakeApi = FakeApiService(
            listWalletsResult = { listOf(wallet) },
            getWalletBalanceResult = { WalletBalanceResponse("wallet-1", "GNF", "0.00") },
            listCardsResult = { listOf(card("card-1")) },
            getUnreadNotificationCountResult = { UnreadCountResponse(0) },
            getKycStatusResult = { KycStatusResponse(null, emptyList(), 2) },
            issueCardResult = { throw RuntimeException("Nombre maximum de cartes atteint (1)") },
        )
        val viewModel = buildViewModel(fakeApi)

        viewModel.issueCard()

        assertEquals("Nombre maximum de cartes atteint (1)", viewModel.actionError.value)
        assertEquals(1, (viewModel.state.value as UiState.Success).data.cards.size)
    }
}
