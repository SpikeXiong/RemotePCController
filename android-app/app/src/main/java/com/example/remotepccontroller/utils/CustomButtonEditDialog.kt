package com.example.remotepccontroller.utils

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import com.example.remotepccontroller.models.CustomButton

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CustomButtonEditDialog(
    button: CustomButton? = null, // null表示新建，非null表示编辑
    onDismiss: () -> Unit,
    onSave: (CustomButton) -> Unit
) {
    var name by remember { mutableStateOf(button?.name ?: "") }
    var endpoint by remember { mutableStateOf(button?.endpoint ?: "") }
    var method by remember { mutableStateOf(button?.method ?: "GET") }
    var successMessage by remember { mutableStateOf(button?.successMessage ?: "命令执行成功") }
    var category by remember { mutableStateOf(button?.category ?: "自定义") }
    var isDangerous by remember { mutableStateOf(button?.isDangerous ?: false) }
    var parametersText by remember {
        mutableStateOf(
            button?.parameters?.map { "${it.key}=${it.value}" }?.joinToString("\n") ?: ""
        )
    }

    // 预定义的分类
    val categories = listOf("自定义", "音量控制", "媒体控制", "亮度控制", "应用程序", "窗口控制", "系统控制", "快捷键")
    var expandedCategory by remember { mutableStateOf(false) }
    var expandedMethod by remember { mutableStateOf(false) }

    Dialog(onDismissRequest = onDismiss) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Column(
                modifier = Modifier
                    .padding(20.dp)
                    .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Text(
                    text = if (button == null) "添加自定义按钮" else "编辑自定义按钮",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold
                )

                // 按钮名称
                OutlinedTextField(
                    value = name,
                    onValueChange = { name = it },
                    label = { Text("按钮名称") },
                    placeholder = { Text("例如: 打开记事本") },
                    modifier = Modifier.fillMaxWidth()
                )

                // API端点
                OutlinedTextField(
                    value = endpoint,
                    onValueChange = { endpoint = it },
                    label = { Text("API端点") },
                    placeholder = { Text("例如: /api/volume/up") },
                    modifier = Modifier.fillMaxWidth()
                )

                // HTTP方法选择
                ExposedDropdownMenuBox(
                    expanded = expandedMethod,
                    onExpandedChange = { expandedMethod = !expandedMethod }
                ) {
                    OutlinedTextField(
                        value = method,
                        onValueChange = { },
                        readOnly = true,
                        label = { Text("HTTP方法") },
                        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expandedMethod) },
                        modifier = Modifier.menuAnchor(
                            type = MenuAnchorType.SecondaryEditable,
                            enabled = true
                        )
                    )
                    ExposedDropdownMenu(
                        expanded = expandedMethod,
                        onDismissRequest = { expandedMethod = false }
                    ) {
                        listOf("GET", "POST").forEach { methodOption ->
                            DropdownMenuItem(
                                text = { Text(methodOption) },
                                onClick = {
                                    method = methodOption
                                    expandedMethod = false
                                }
                            )
                        }
                    }
                }

                // 参数设置
                OutlinedTextField(
                    value = parametersText,
                    onValueChange = { parametersText = it },
                    label = { Text("参数 (可选)") },
                    placeholder = { Text("每行一个参数，格式: key=value\n例如:\nsteps=5\nforce=true") },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(100.dp),
                    maxLines = 5
                )

                // 成功消息
                OutlinedTextField(
                    value = successMessage,
                    onValueChange = { successMessage = it },
                    label = { Text("成功消息") },
                    placeholder = { Text("操作成功时显示的消息") },
                    modifier = Modifier.fillMaxWidth()
                )

                // 分类选择
                ExposedDropdownMenuBox(
                    expanded = expandedCategory,
                    onExpandedChange = { expandedCategory = !expandedCategory }
                ) {
                    OutlinedTextField(
                        value = category,
                        onValueChange = { category = it },
                        label = { Text("分类") },
                        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expandedCategory) },
                        modifier = Modifier.menuAnchor(
                            type = MenuAnchorType.SecondaryEditable,
                            enabled = true
                        )
                    )
                    ExposedDropdownMenu(
                        expanded = expandedCategory,
                        onDismissRequest = { expandedCategory = false }
                    ) {
                        categories.forEach { categoryOption ->
                            DropdownMenuItem(
                                text = { Text(categoryOption) },
                                onClick = {
                                    category = categoryOption
                                    expandedCategory = false
                                }
                            )
                        }
                    }
                }

                // 危险操作开关
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("危险操作 (红色按钮)")
                    Switch(
                        checked = isDangerous,
                        onCheckedChange = { isDangerous = it }
                    )
                }

                HorizontalDivider()

                // 按钮操作
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.End,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    TextButton(onClick = onDismiss) {
                        Text("取消")
                    }

                    Spacer(modifier = Modifier.width(8.dp))

                    Button(
                        onClick = {
                            if (name.isNotBlank() && endpoint.isNotBlank()) {
                                // 解析参数
                                val parameters = parametersText
                                    .lines()
                                    .filter { it.isNotBlank() && it.contains("=") }
                                    .associate {
                                        val parts = it.split("=", limit = 2)
                                        parts[0].trim() to parts[1].trim()
                                    }

                                val newButton = CustomButton(
                                    id = button?.id ?: "",
                                    name = name,
                                    endpoint = endpoint,
                                    method = method,
                                    parameters = parameters,
                                    successMessage = successMessage,
                                    category = category,
                                    isDangerous = isDangerous
                                )
                                onSave(newButton)
                            }
                        },
                        enabled = name.isNotBlank() && endpoint.isNotBlank()
                    ) {
                        Text("保存")
                    }
                }
            }
        }
    }
}
