package com.nasrcash.app.ui.support

import com.nasrcash.app.MainDispatcherRule
import com.nasrcash.app.core.network.FakeApiService
import com.nasrcash.app.core.network.TicketResponse
import com.nasrcash.app.data.repository.SupportRepository
import com.nasrcash.app.ui.common.UiState
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test

class SupportListViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private fun ticket(id: String, subject: String) = TicketResponse(
        id = id, user_id = "user-1", subject = subject, category = "general",
        status = "open", created_at = "2026-01-01T00:00:00Z",
    )

    @Test
    fun `load populates ticket list on success`() = runTest {
        val fakeApi = FakeApiService(listTicketsResult = { listOf(ticket("t1", "Recharge non reçue")) })
        val viewModel = SupportListViewModel(SupportRepository(fakeApi))

        val state = viewModel.state.value
        assertTrue(state is UiState.Success)
        assertEquals(1, (state as UiState.Success).data.size)
        assertEquals("Recharge non reçue", state.data.first().subject)
    }

    @Test
    fun `load surfaces an error message on failure`() = runTest {
        val fakeApi = FakeApiService(listTicketsResult = { throw RuntimeException("Backend indisponible") })
        val viewModel = SupportListViewModel(SupportRepository(fakeApi))

        val state = viewModel.state.value
        assertTrue(state is UiState.Error)
        assertEquals("Backend indisponible", (state as UiState.Error).message)
    }

    @Test
    fun `createTicket rejects a blank subject without calling the API`() = runTest {
        val fakeApi = FakeApiService(listTicketsResult = { emptyList() })
        val viewModel = SupportListViewModel(SupportRepository(fakeApi))

        var createdId: String? = null
        viewModel.createTicket(subject = "", category = "general", message = "Bonjour") { createdId = it }

        assertEquals("Sujet et message sont requis", viewModel.actionError.value)
        assertNull(createdId)
    }

    @Test
    fun `createTicket calls back with the new ticket id on success`() = runTest {
        val fakeApi = FakeApiService(
            listTicketsResult = { emptyList() },
            createTicketResult = { ticket("new-ticket-id", it.subject) },
        )
        val viewModel = SupportListViewModel(SupportRepository(fakeApi))

        var createdId: String? = null
        viewModel.createTicket(subject = "Carte bloquée", category = "card", message = "Aidez-moi") {
            createdId = it
        }

        assertEquals("new-ticket-id", createdId)
        assertNull(viewModel.actionError.value)
    }

    @Test
    fun `createTicket surfaces the backend error and does not invoke the callback`() = runTest {
        val fakeApi = FakeApiService(
            listTicketsResult = { emptyList() },
            createTicketResult = { throw RuntimeException("Catégorie de ticket invalide : bogus") },
        )
        val viewModel = SupportListViewModel(SupportRepository(fakeApi))

        var createdId: String? = null
        viewModel.createTicket(subject = "Test", category = "bogus", message = "...") { createdId = it }

        assertEquals("Catégorie de ticket invalide : bogus", viewModel.actionError.value)
        assertNull(createdId)
    }
}
