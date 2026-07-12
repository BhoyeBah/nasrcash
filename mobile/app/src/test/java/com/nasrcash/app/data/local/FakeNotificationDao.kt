package com.nasrcash.app.data.local

import kotlinx.coroutines.flow.MutableStateFlow

class FakeNotificationDao : NotificationDao {
    private val entities = MutableStateFlow<List<NotificationEntity>>(emptyList())

    override fun observeAll() = entities

    override suspend fun upsertAll(notifications: List<NotificationEntity>) {
        val byId = entities.value.associateBy { it.id }.toMutableMap()
        notifications.forEach { byId[it.id] = it }
        entities.value = byId.values.sortedByDescending { it.createdAt }
    }

    override suspend fun clear() {
        entities.value = emptyList()
    }
}
