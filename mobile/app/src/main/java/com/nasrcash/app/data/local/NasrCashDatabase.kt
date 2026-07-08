package com.nasrcash.app.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(entities = [NotificationEntity::class], version = 1, exportSchema = false)
abstract class NasrCashDatabase : RoomDatabase() {
    abstract fun notificationDao(): NotificationDao

    companion object {
        @Volatile private var instance: NasrCashDatabase? = null

        fun getInstance(context: Context): NasrCashDatabase =
            instance ?: synchronized(this) {
                instance ?: Room.databaseBuilder(
                    context.applicationContext,
                    NasrCashDatabase::class.java,
                    "nasrcash.db",
                ).build().also { instance = it }
            }
    }
}
