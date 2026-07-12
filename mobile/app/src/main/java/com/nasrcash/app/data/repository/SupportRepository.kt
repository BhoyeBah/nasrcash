package com.nasrcash.app.data.repository

import com.nasrcash.app.core.network.ApiResult
import com.nasrcash.app.core.network.ApiService
import com.nasrcash.app.core.network.MessageCreateRequest
import com.nasrcash.app.core.network.TicketCreateRequest
import com.nasrcash.app.core.network.TicketDetailResponse
import com.nasrcash.app.core.network.TicketMessageResponse
import com.nasrcash.app.core.network.TicketResponse
import com.nasrcash.app.core.network.safeApiCall

class SupportRepository(private val apiService: ApiService) {

    suspend fun createTicket(subject: String, category: String, message: String): ApiResult<TicketResponse> =
        safeApiCall { apiService.createTicket(TicketCreateRequest(subject, category, message)) }

    suspend fun listTickets(): ApiResult<List<TicketResponse>> = safeApiCall { apiService.listTickets() }

    suspend fun getTicket(ticketId: String): ApiResult<TicketDetailResponse> =
        safeApiCall { apiService.getTicket(ticketId) }

    suspend fun addMessage(ticketId: String, body: String): ApiResult<TicketMessageResponse> =
        safeApiCall { apiService.addTicketMessage(ticketId, MessageCreateRequest(body)) }
}
