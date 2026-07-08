package com.nasrcash.app.data.repository

import com.nasrcash.app.core.network.ApiResult
import com.nasrcash.app.core.network.ApiService
import com.nasrcash.app.core.network.NotificationResponse
import com.nasrcash.app.core.network.safeApiCall
import com.nasrcash.app.data.local.NotificationDao
import com.nasrcash.app.data.local.NotificationEntity
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

class NotificationRepository(
    private val apiService: ApiService,
    private val notificationDao: NotificationDao,
) {
    /** Cached notifications for instant, offline-friendly display. */
    fun observeCached(): Flow<List<NotificationResponse>> =
        notificationDao.observeAll().map { entities ->
            entities.map { NotificationResponse(it.id, it.type, it.title, it.body, it.readAt, it.createdAt) }
        }

    /** Refreshes the cache from the backend — the source of truth. */
    suspend fun refresh(): ApiResult<Unit> = safeApiCall {
        val remote = apiService.listNotifications()
        notificationDao.upsertAll(
            remote.map { NotificationEntity(it.id, it.type, it.title, it.body, it.read_at, it.created_at) },
        )
    }

    suspend fun getUnreadCount(): ApiResult<Int> = safeApiCall { apiService.getUnreadNotificationCount().unread_count }

    suspend fun markRead(notificationId: String): ApiResult<Unit> = safeApiCall {
        val updated = apiService.markNotificationRead(notificationId)
        notificationDao.upsertAll(
            listOf(
                NotificationEntity(
                    updated.id, updated.type, updated.title, updated.body, updated.read_at, updated.created_at,
                ),
            ),
        )
    }
}
