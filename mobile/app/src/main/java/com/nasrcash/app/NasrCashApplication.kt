package com.nasrcash.app

import android.app.Application
import com.nasrcash.app.core.di.AppContainer

class NasrCashApplication : Application() {
    lateinit var container: AppContainer
        private set

    override fun onCreate() {
        super.onCreate()
        container = AppContainer(this)
    }
}
