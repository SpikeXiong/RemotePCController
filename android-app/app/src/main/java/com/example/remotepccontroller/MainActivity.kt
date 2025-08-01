package com.example.remotepccontroller

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import com.example.remotepccontroller.ui.theme.RemotePCControllerTheme

import android.widget.Toast
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.graphics.Color
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.ui.Alignment
import com.example.remotepccontroller.models.CustomButton
import com.example.remotepccontroller.network.NetworkService
import com.example.remotepccontroller.utils.CustomButtonEditDialog
import com.example.remotepccontroller.utils.CustomButtonManager
import com.example.remotepccontroller.utils.TemplateSelectionDialog

class MainActivity : ComponentActivity() {
    private lateinit var networkService: NetworkService
    private lateinit var customButtonManager: CustomButtonManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        networkService = NetworkService()
        customButtonManager = CustomButtonManager(this)

        enableEdgeToEdge()
        setContent {
            RemotePCControllerTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    RemoteControlScreen(
                        networkService = networkService,
                        customButtonManager = customButtonManager,
                        modifier = Modifier.padding(innerPadding)
                    )
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RemoteControlScreen(
    networkService: NetworkService,
    customButtonManager: CustomButtonManager,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    var serverUrl by remember { mutableStateOf("192.168.31.109:8090") }
    var isConnected by remember { mutableStateOf(false) }

    // 自定义按钮相关状态
    var customButtons by remember { mutableStateOf(customButtonManager.loadButtons()) }
    var showEditDialog by remember { mutableStateOf(false) }
    var showTemplateDialog by remember { mutableStateOf(false) }
    var editingButton by remember { mutableStateOf<CustomButton?>(null) }
    var addButton by remember {mutableStateOf(value = false)}
    // 显示Toast消息的函数
    fun showToast(message: String) {
        Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
    }

    // 发送命令的函数（更新为支持自定义参数）
    fun sendCommand(endpoint: String, method: String = "GET", parameters: Map<String, String> = emptyMap(), successMessage: String = "命令执行成功") {
        networkService.sendCommand(endpoint, method, parameters) { success, message ->
            (context as ComponentActivity).runOnUiThread {
                if (success) {
                    showToast(successMessage)
                } else {
                    showToast("错误: $message")
                }
            }
        }
    }

    // 执行自定义按钮
    fun executeCustomButton(button: CustomButton) {
        sendCommand(button.endpoint, button.method, button.parameters, button.successMessage)
    }

    // 刷新自定义按钮列表
    fun refreshCustomButtons() {
        customButtons = customButtonManager.loadButtons()
    }

    // 编辑对话框
    if (showEditDialog) {
        CustomButtonEditDialog(
            button = editingButton,
            onDismiss = {
                showEditDialog = false
                editingButton = null
            },
            onSave = { button ->
                if (editingButton == null || addButton) {
                    customButtonManager.addButton(button)
                    showToast("自定义按钮已添加")
                } else {
                    customButtonManager.updateButton(button)
                    showToast("自定义按钮已更新")
                }
                refreshCustomButtons()
                showEditDialog = false
                editingButton = null
                addButton = false
            }
        )
    }

    // 模板选择对话框
    if (showTemplateDialog) {
        TemplateSelectionDialog(
            onDismiss = { showTemplateDialog = false },
            onTemplateSelected = { template ->
                editingButton = template
                showTemplateDialog = false
                showEditDialog = true
                addButton = true
            }
        )
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // 服务器连接设置
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = if (isConnected)
                    MaterialTheme.colorScheme.primaryContainer
                else
                    MaterialTheme.colorScheme.surface
            )
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text = "服务器设置",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold
                    )

                    Box(
                        modifier = Modifier
                            .size(12.dp)
                            .padding(2.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Card(
                            modifier = Modifier.fillMaxSize(),
                            colors = CardDefaults.cardColors(
                                containerColor = if (isConnected) Color.Green else Color.Red
                            )
                        ) {}
                    }
                }

                OutlinedTextField(
                    value = serverUrl,
                    onValueChange = {
                        serverUrl = it
                        isConnected = false
                    },
                    label = { Text("PC服务器地址") },
                    placeholder = { Text("192.168.31.109:8090") },
                    modifier = Modifier.fillMaxWidth()
                )

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Button(
                        onClick = {
                            networkService.setServerUrl(serverUrl)
                            showToast("服务器地址已更新")
                        },
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("设置地址")
                    }

                    OutlinedButton(
                        onClick = {
                            networkService.setServerUrl(serverUrl)
                            networkService.sendCommand("/api/test") { success, message ->
                                (context as ComponentActivity).runOnUiThread {
                                    isConnected = success
                                    showToast(if (success) "连接成功!" else "连接失败: $message")
                                }
                            }
                        },
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("测试连接")
                    }
                }
            }
        }

        // 自定义按钮管理
        Card(
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = "🎛️ 自定义按钮管理",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Button(
                        onClick = {
                            editingButton = null
                            showEditDialog = true
                        },
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("新建按钮")
                    }

                    OutlinedButton(
                        onClick = { showTemplateDialog = true },
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("使用模板")
                    }
                }
            }
        }

        // 显示自定义按钮（按分类分组）
        val customButtonsByCategory = customButtons.groupBy { it.category }
        customButtonsByCategory.forEach { (category, buttons) ->
            CustomControlSection(
                title = "🎯 $category",
                buttons = buttons,
                onButtonClick = { executeCustomButton(it) },
                onButtonEdit = { button ->
                    editingButton = button
                    showEditDialog = true
                },
                onButtonDelete = { button ->
                    customButtonManager.deleteButton(button.id)
                    refreshCustomButtons()
                    showToast("按钮已删除")
                }
            )
        }

        // 原有的控制区域保持不变
        ControlSection(
            title = "🔊 音量控制",
            buttons = listOf(
                "音量 +" to { sendCommand("/api/volume/up", "GET", emptyMap(), "音量已增加") },
                "音量 -" to { sendCommand("/api/volume/down", "GET", emptyMap(), "音量已降低") },
                "静音" to { sendCommand("/api/volume/mute", "GET", emptyMap(), "静音状态已切换") }
            )
        )

        ControlSection(
            title = "🎵 媒体控制",
            buttons = listOf(
                "播放/暂停" to { sendCommand("/api/media/play", "GET", emptyMap(), "播放/暂停") },
                "停止" to { sendCommand("/api/media/stop", "GET", emptyMap(), "媒体已停止") },
                "下一首" to { sendCommand("/api/media/next", "GET", emptyMap(), "下一首") },
                "上一首" to { sendCommand("/api/media/previous", "GET", emptyMap(), "上一首") }
            )
        )

        ControlSection(
            title = "💡 屏幕亮度",
            buttons = listOf(
                "亮度 +" to { sendCommand("/api/brightness/up", "GET", emptyMap(), "亮度已增加") },
                "亮度 -" to { sendCommand("/api/brightness/down", "GET", emptyMap(), "亮度已降低") }
            )
        )

        ControlSection(
            title = "🪟 窗口控制",
            buttons = listOf(
                "最小化" to { sendCommand("/api/window/minimize", "GET", emptyMap(), "窗口已最小化") },
                "最大化" to { sendCommand("/api/window/maximize", "GET", emptyMap(), "窗口已最大化") },
                "恢复窗口" to { sendCommand("/api/window/restore", "GET", emptyMap(), "窗口已恢复") },
                "关闭窗口" to { sendCommand("/api/window/close", "GET", emptyMap(), "窗口已关闭") }
            )
        )

        ControlSection(
            title = "⌨️ 快捷键",
            buttons = listOf(
                "Alt+Tab" to { sendCommand("/api/hotkey/alt_tab", "GET", emptyMap(), "Alt+Tab") },
                "Win+D" to { sendCommand("/api/hotkey/win_d", "GET", emptyMap(), "显示桌面") },
                "Ctrl+C" to { sendCommand("/api/hotkey/ctrl_c", "GET", emptyMap(), "复制") },
                "Ctrl+V" to { sendCommand("/api/hotkey/ctrl_v", "GET", emptyMap(), "粘贴") }
            )
        )

        ControlSection(
            title = "💻 系统控制",
            buttons = listOf(
                "锁定屏幕" to { sendCommand("/api/system/lock", "GET", emptyMap(), "屏幕已锁定") },
                "系统信息" to { sendCommand("/api/system/info", "GET", emptyMap(), "获取系统信息") },
                "休眠" to { sendCommand("/api/system/sleep", "GET", emptyMap(), "系统休眠") }
            ),
            dangerousButtons = listOf("休眠")
        )

        ControlSection(
            title = "📱 应用控制",
            buttons = listOf(
                "获取进程" to { sendCommand("/api/app/processes", "GET", emptyMap(), "获取进程列表") }
            )
        )
    }
}

// 自定义按钮控制区域组件
@Composable
fun CustomControlSection(
    title: String,
    buttons: List<CustomButton>,
    onButtonClick: (CustomButton) -> Unit,
    onButtonEdit: (CustomButton) -> Unit,
    onButtonDelete: (CustomButton) -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = title,
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold
            )

            buttons.forEach { button ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // 主按钮
                    Button(
                        onClick = { onButtonClick(button) },
                        modifier = Modifier
                            .weight(1f)
                            .height(56.dp),
                        colors = if (button.isDangerous) {
                            ButtonDefaults.buttonColors(
                                containerColor = MaterialTheme.colorScheme.error
                            )
                        } else {
                            ButtonDefaults.buttonColors()
                        }
                    ) {
                        Text(
                            text = button.name,
                            color = if (button.isDangerous) Color.White else MaterialTheme.colorScheme.onPrimary
                        )
                    }

                    // 编辑按钮
                    IconButton(
                        onClick = { onButtonEdit(button) },
                        modifier = Modifier.size(48.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Edit,
                            contentDescription = "编辑",
                            tint = MaterialTheme.colorScheme.primary
                        )
                    }

                    // 删除按钮
                    IconButton(
                        onClick = { onButtonDelete(button) },
                        modifier = Modifier.size(48.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Delete,
                            contentDescription = "删除",
                            tint = MaterialTheme.colorScheme.error
                        )
                    }
                }
            }
        }
    }
}

// 原有的控制区域组件保持不变
@Composable
fun ControlSection(
    title: String,
    buttons: List<Pair<String, () -> Unit>>,
    dangerousButtons: List<String> = emptyList(),
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = title,
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold
            )

            val chunkedButtons = buttons.chunked(2)
            chunkedButtons.forEach { rowButtons ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    rowButtons.forEach { (text, onClick) ->
                        val isDangerous = dangerousButtons.contains(text)

                        if (isDangerous) {
                            Button(
                                onClick = onClick,
                                modifier = Modifier
                                    .weight(1f)
                                    .height(56.dp),
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = MaterialTheme.colorScheme.error
                                )
                            ) {
                                Text(text, color = Color.White)
                            }
                        } else {
                            Button(
                                onClick = onClick,
                                modifier = Modifier
                                    .weight(1f)
                                    .height(56.dp)
                            ) {
                                Text(text)
                            }
                        }
                    }

                    if (rowButtons.size == 1) {
                        Spacer(modifier = Modifier.weight(1f))
                    }
                }
            }
        }
    }
}

@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    RemotePCControllerTheme {
        RemoteControlScreen(
            networkService = NetworkService(),
            customButtonManager = CustomButtonManager(LocalContext.current)
        )
    }
}
