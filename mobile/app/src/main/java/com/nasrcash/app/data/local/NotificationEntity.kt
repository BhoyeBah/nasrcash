package com.nasrcash.app.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

/** Local cache of notifications for offline viewing — non-sensitive data only. */
@Entity(tableName = "notifications")
data class NotificationEntity(
    @PrimaryKey val id: String,
    val type: String,
    val title: String,
    val body: String,
    val readAt: String?,
    val createdAt: String,
)
