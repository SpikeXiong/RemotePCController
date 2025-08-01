package com.example.remotepccontroller.utils

import android.content.Context
import android.content.SharedPreferences
import androidx.core.content.edit
import com.example.remotepccontroller.models.CustomButton
import kotlinx.serialization.json.Json
import java.util.UUID

class CustomButtonManager(context: Context) {
    private val prefs: SharedPreferences = context.getSharedPreferences("custom_buttons", Context.MODE_PRIVATE)
    private val json = Json { ignoreUnknownKeys = true }

    companion object {
        private const val BUTTONS_KEY = "custom_buttons"
    }

    fun saveButtons(buttons: List<CustomButton>) {
        val jsonString = json.encodeToString(buttons)
        prefs.edit {
            putString(BUTTONS_KEY, jsonString)
        }
    }

    fun loadButtons(): List<CustomButton> {
        val jsonString = prefs.getString(BUTTONS_KEY, null) ?: return emptyList()
        return try {
            json.decodeFromString<List<CustomButton>>(jsonString)
        } catch (_: Exception) {
            emptyList()
        }
    }

    fun addButton(button: CustomButton): CustomButton {
        val newButton = button.copy(id = button.id.ifEmpty { UUID.randomUUID().toString() })
        val currentButtons = loadButtons().toMutableList()
        currentButtons.add(newButton)
        saveButtons(currentButtons)
        return newButton
    }

    fun updateButton(button: CustomButton) {
        val currentButtons = loadButtons().toMutableList()
        val index = currentButtons.indexOfFirst { it.id == button.id }
        if (index != -1) {
            currentButtons[index] = button
            saveButtons(currentButtons)
        }
    }

    fun deleteButton(buttonId: String) {
        val currentButtons = loadButtons().toMutableList()
        currentButtons.removeAll { it.id == buttonId }
        saveButtons(currentButtons)
    }

}
