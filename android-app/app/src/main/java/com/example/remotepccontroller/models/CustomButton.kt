package com.example.remotepccontroller.models

import kotlinx.serialization.Serializable

@Serializable
data class CustomButton(
    val id: String = "",
    val name: String = "",
    val endpoint: String = "",
    val method: String = "GET", // GET 或 POST
    val parameters: Map<String, String> = emptyMap(),
    val successMessage: String = "命令执行成功",
    val category: String = "自定义", // 按钮分类
    val isDangerous: Boolean = false // 是否为危险操作
)

// 预设的一些常用自定义按钮模板
object CustomButtonTemplates {
    val templates = listOf(
        CustomButton(
            id = "notepad",
            name = "打开记事本",
            endpoint = "/api/app/launch",
            method = "POST",
            parameters = mapOf("path" to "C:\\Windows\\System32\\notepad.exe"),
            successMessage = "记事本已启动",
            category = "应用程序"
        ),
        CustomButton(
            id = "calculator",
            name = "打开计算器",
            endpoint = "/api/app/launch",
            method = "POST",
            parameters = mapOf("path" to "C:\\Windows\\System32\\calc.exe"),
            successMessage = "计算器已启动",
            category = "应用程序"
        ),
        CustomButton(
            id = "chrome",
            name = "打开Chrome",
            endpoint = "/api/app/launch",
            method = "POST",
            parameters = mapOf("path" to "chrome.exe"),
            successMessage = "Chrome已启动",
            category = "应用程序"
        ),
        CustomButton(
            id = "volume_up_5",
            name = "音量+5",
            endpoint = "/api/volume/up",
            method = "POST",
            parameters = mapOf("steps" to "5"),
            successMessage = "音量增加5级",
            category = "音量控制"
        ),
        CustomButton(
            id = "brightness_up_10",
            name = "亮度+10",
            endpoint = "/api/brightness/up",
            method = "POST",
            parameters = mapOf("steps" to "10"),
            successMessage = "亮度增加10级",
            category = "亮度控制"
        ),
        CustomButton(
            id = "shutdown_force",
            name = "强制关机",
            endpoint = "/api/system/shutdown",
            method = "POST",
            parameters = mapOf("force" to "true"),
            successMessage = "系统将强制关机",
            category = "系统控制",
            isDangerous = true
        )
    )
}
