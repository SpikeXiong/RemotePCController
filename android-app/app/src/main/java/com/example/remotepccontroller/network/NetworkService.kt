package com.example.remotepccontroller.network

import okhttp3.*
import okhttp3.HttpUrl.Companion.toHttpUrlOrNull
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException

class NetworkService {
    private val client = OkHttpClient()
    private var baseUrl = "http://192.168.31.165:8090"

    fun setServerUrl(url: String) {
        baseUrl = if (url.startsWith("http://") || url.startsWith("https://")) {
            url
        } else {
            "http://$url"
        }
    }

    fun sendCommand(
        endpoint: String,
        method: String = "GET",
        parameters: Map<String, String> = emptyMap(),
        callback: (Boolean, String) -> Unit
    ) {
        val url = "$baseUrl$endpoint"

        val request = when (method.uppercase()) {
            "POST" -> {
                val jsonBody = if (parameters.isNotEmpty()) {
                    JSONObject(parameters).toString()
                } else {
                    "{}"
                }

                Request.Builder()
                    .url(url)
                    .post(jsonBody.toRequestBody("application/json".toMediaType()))
                    .build()
            }
            else -> { // GET
                val urlBuilder = url.toHttpUrlOrNull()?.newBuilder()
                parameters.forEach { (key, value) ->
                    urlBuilder?.addQueryParameter(key, value)
                }

                val finalUrl: String = urlBuilder?.build()?.toString() ?: url
                Request.Builder()
                    .url(finalUrl)
                    .build() // 添加这行！
            }
        }

        // 移除类型转换，因为request现在已经是Request类型
        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                callback(false, "网络错误: ${e.message}")
            }

            override fun onResponse(call: Call, response: Response) {
                try {
                    val responseBody = response.body?.string() ?: ""
                    if (response.isSuccessful) {
                        val jsonResponse = JSONObject(responseBody)
                        val success = jsonResponse.optBoolean("success", true)
                        val message = jsonResponse.optString("message", "操作完成")
                        callback(success, message)
                    } else {
                        callback(false, "服务器错误: ${response.code}")
                    }
                } catch (e: Exception) {
                    callback(false, "响应解析错误: ${e.message}")
                }
            }
        })
    }
}
