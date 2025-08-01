import ctypes
from ctypes import wintypes
from enum import Enum
import time
import os
import subprocess
import logging
from typing import Optional, Union, Dict, List, Tuple
import json
from dataclasses import dataclass
import shutil

class SystemKey(Enum):
    """系统控制按键枚举"""
    # 音量控制
    VOLUME_UP = 0xAF
    VOLUME_DOWN = 0xAE
    VOLUME_MUTE = 0xAD
    
    # 媒体控制
    MEDIA_PLAY_PAUSE = 0xB3
    MEDIA_STOP = 0xB2
    MEDIA_NEXT = 0xB0
    MEDIA_PREV = 0xB1
    
    # 系统控制
    BRIGHTNESS_UP = 0xE9
    BRIGHTNESS_DOWN = 0xE8
    
    # 功能键
    F1 = 0x70
    F2 = 0x71
    F3 = 0x72
    F4 = 0x73
    F5 = 0x74
    F6 = 0x75
    F7 = 0x76
    F8 = 0x77
    F9 = 0x78
    F10 = 0x79
    F11 = 0x7A
    F12 = 0x7B

class WindowState(Enum):
    """窗口状态枚举"""
    HIDE = 0
    NORMAL = 1
    MINIMIZED = 2
    MAXIMIZED = 3
    RESTORE = 9

@dataclass
class ProcessInfo:
    """进程信息"""
    pid: int
    name: str
    executable: str
    memory_usage: int

@dataclass
class WindowInfo:
    """窗口信息"""
    hwnd: int
    title: str
    class_name: str
    rect: Tuple[int, int, int, int]
    is_visible: bool

class WindowsSystemController:
    """Windows 系统控制器 - 全功能版本"""
    
    def __init__(self):
        """初始化系统控制器"""
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        self.shell32 = ctypes.windll.shell32
        self.psapi = ctypes.windll.psapi
        self._logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger('SystemController')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _send_key_event(self, key_code: int, delay: float = 0.05) -> bool:
        """发送键盘事件"""
        try:
            self.user32.keybd_event(key_code, 0, 0, 0)
            time.sleep(delay)
            self.user32.keybd_event(key_code, 0, 2, 0)
            return True
        except Exception as e:
            self._logger.error(f"发送键盘事件失败: {e}")
            return False
    
    # =================== 音量控制 ===================
    def volume_up(self, steps: int = 1) -> dict:
        """增加音量"""
        return self._volume_control('up', steps)
    
    def volume_down(self, steps: int = 1) -> dict:
        """降低音量"""
        return self._volume_control('down', steps)
    
    def volume_mute(self) -> dict:
        """切换静音"""
        try:
            if self._send_key_event(SystemKey.VOLUME_MUTE.value):
                return {'success': True, 'message': '静音状态已切换', 'action': 'volume_mute'}
            return {'success': False, 'message': '静音切换失败'}
        except Exception as e:
            return {'success': False, 'message': f'静音操作失败: {str(e)}'}
    
    def _volume_control(self, action: str, steps: int) -> dict:
        """音量控制核心方法"""
        try:
            key_code = SystemKey.VOLUME_UP.value if action == 'up' else SystemKey.VOLUME_DOWN.value
            
            for i in range(steps):
                if not self._send_key_event(key_code):
                    return {'success': False, 'message': f'音量{action}失败，在第{i + 1}步'}
                if steps > 1:
                    time.sleep(0.1)
            
            return {
                'success': True,
                'message': f'音量已{"增加" if action == "up" else "降低"} {steps} 步',
                'action': f'volume_{action}',
                'steps': steps
            }
        except Exception as e:
            return {'success': False, 'message': f'音量{action}操作失败: {str(e)}'}
    
    # =================== 媒体控制 ===================
    def media_play_pause(self) -> dict:
        """播放/暂停媒体"""
        return self._media_control('play_pause', SystemKey.MEDIA_PLAY_PAUSE)
    
    def media_stop(self) -> dict:
        """停止媒体"""
        return self._media_control('stop', SystemKey.MEDIA_STOP)
    
    def media_next(self) -> dict:
        """下一首"""
        return self._media_control('next', SystemKey.MEDIA_NEXT)
    
    def media_previous(self) -> dict:
        """上一首"""
        return self._media_control('previous', SystemKey.MEDIA_PREV)
    
    def _media_control(self, action: str, key: SystemKey) -> dict:
        """媒体控制核心方法"""
        try:
            if self._send_key_event(key.value):
                return {'success': True, 'message': f'媒体{action}命令已发送', 'action': f'media_{action}'}
            return {'success': False, 'message': f'媒体{action}失败'}
        except Exception as e:
            return {'success': False, 'message': f'媒体{action}操作失败: {str(e)}'}
    
    # =================== 屏幕亮度控制 ===================
    def brightness_up(self, steps: int = 1) -> dict:
        """增加屏幕亮度"""
        return self._brightness_control('up', steps)
    
    def brightness_down(self, steps: int = 1) -> dict:
        """降低屏幕亮度"""
        return self._brightness_control('down', steps)
    
    def _brightness_control(self, action: str, steps: int) -> dict:
        """亮度控制核心方法"""
        try:
            key_code = SystemKey.BRIGHTNESS_UP.value if action == 'up' else SystemKey.BRIGHTNESS_DOWN.value
            
            for i in range(steps):
                if not self._send_key_event(key_code):
                    return {'success': False, 'message': f'亮度{action}失败，在第{i + 1}步'}
                if steps > 1:
                    time.sleep(0.2)
            
            return {
                'success': True,
                'message': f'屏幕亮度已{"增加" if action == "up" else "降低"} {steps} 步',
                'action': f'brightness_{action}',
                'steps': steps
            }
        except Exception as e:
            return {'success': False, 'message': f'亮度{action}操作失败: {str(e)}'}
    
    # =================== 应用程序控制 ===================
    def app_exists(self, app_path):
        # 先判断是否是绝对路径
        if os.path.isabs(app_path):
            return os.path.exists(app_path)
        # 否则尝试在 PATH 里查找
        return shutil.which(app_path) is not None

    def launch_application(self, app_path: str, args: str = "", working_dir: str = "") -> dict:
        """启动应用程序"""
        try:

            if not self.app_exists(app_path):
                print(f'应用程序不存在')

                return {'success': False, 'message': f'应用程序不存在: {app_path}'}
            
            command = f'"{app_path}"'
            if args:
                command += f' {args}'
            
            print(f'dd {command}')

            process = subprocess.Popen(
                command,
                cwd=working_dir if working_dir else None,
                shell=True
            )
            
            return {
                'success': True,
                'message': f'应用程序已启动: {os.path.basename(app_path)}',
                'pid': process.pid,
                'action': 'launch_app'
            }
        except Exception as e:
            print( f'启动应用程序失败: {str(e)}')
            return {'success': False, 'message': f'启动应用程序失败: {str(e)}'}
    
    def kill_process(self, process_name: str) -> dict:
        """终止进程"""
        try:
            result = subprocess.run(['taskkill', '/f', '/im', process_name], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': f'进程已终止: {process_name}',
                    'action': 'kill_process'
                }
            else:
                return {
                    'success': False,
                    'message': f'终止进程失败: {result.stderr.strip()}'
                }
        except Exception as e:
            return {'success': False, 'message': f'终止进程操作失败: {str(e)}'}
    
    def get_running_processes(self) -> dict:
        """获取运行中的进程列表"""
        try:
            result = subprocess.run(['tasklist', '/fo', 'csv'], 
                                  capture_output=True, text=True, encoding='gbk')
            
            if result.returncode != 0:
                return {'success': False, 'message': '获取进程列表失败'}
            
            lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
            processes = []
            
            for line in lines:
                parts = line.split('","')
                if len(parts) >= 5:
                    name = parts[0].strip('"')
                    pid = parts[1].strip('"')
                    memory = parts[4].strip('"').replace(',', '').replace(' K', '')
                    
                    try:
                        processes.append({
                            'name': name,
                            'pid': int(pid),
                            'memory_kb': int(memory) if memory.isdigit() else 0
                        })
                    except ValueError:
                        continue
            
            return {
                'success': True,
                'message': f'获取到 {len(processes)} 个进程',
                'processes': processes[:50],  # 限制返回数量
                'total_count': len(processes)
            }
        except Exception as e:
            return {'success': False, 'message': f'获取进程列表失败: {str(e)}'}
    
    # =================== 窗口控制 ===================
    def get_active_window(self) -> dict:
        """获取当前活动窗口信息"""
        try:
            hwnd = self.user32.GetForegroundWindow()
            if not hwnd:
                return {'success': False, 'message': '无法获取活动窗口'}
            
            # 获取窗口标题
            title_length = self.user32.GetWindowTextLengthW(hwnd)
            title_buffer = ctypes.create_unicode_buffer(title_length + 1)
            self.user32.GetWindowTextW(hwnd, title_buffer, title_length + 1)
            
            # 获取窗口类名
            class_buffer = ctypes.create_unicode_buffer(256)
            self.user32.GetClassNameW(hwnd, class_buffer, 256)
            
            # 获取窗口位置和大小
            rect = wintypes.RECT()
            self.user32.GetWindowRect(hwnd, ctypes.byref(rect))
            
            return {
                'success': True,
                'window': {
                    'hwnd': hwnd,
                    'title': title_buffer.value,
                    'class_name': class_buffer.value,
                    'rect': {
                        'left': rect.left,
                        'top': rect.top,
                        'right': rect.right,
                        'bottom': rect.bottom,
                        'width': rect.right - rect.left,
                        'height': rect.bottom - rect.top
                    },
                    'is_visible': bool(self.user32.IsWindowVisible(hwnd))
                }
            }
        except Exception as e:
            return {'success': False, 'message': f'获取活动窗口失败: {str(e)}'}
    
    def minimize_window(self, hwnd: Optional[int] = None) -> dict:
        """最小化窗口"""
        return self._control_window('minimize', WindowState.MINIMIZED, hwnd)
    
    def maximize_window(self, hwnd: Optional[int] = None) -> dict:
        """最大化窗口"""
        return self._control_window('maximize', WindowState.MAXIMIZED, hwnd)
    
    def restore_window(self, hwnd: Optional[int] = None) -> dict:
        """恢复窗口"""
        return self._control_window('restore', WindowState.RESTORE, hwnd)
    
    def close_window(self, hwnd: Optional[int] = None) -> dict:
        """关闭窗口"""
        try:
            if hwnd is None:
                hwnd = self.user32.GetForegroundWindow()
            
            if not hwnd:
                return {'success': False, 'message': '无法获取目标窗口'}
            
            # 发送关闭消息
            WM_CLOSE = 0x0010
            self.user32.SendMessageW(hwnd, WM_CLOSE, 0, 0)
            
            return {
                'success': True,
                'message': '窗口关闭命令已发送',
                'action': 'close_window',
                'hwnd': hwnd
            }
        except Exception as e:
            return {'success': False, 'message': f'关闭窗口失败: {str(e)}'}
    
    def _control_window(self, action: str, state: WindowState, hwnd: Optional[int] = None) -> dict:
        """窗口控制核心方法"""
        try:
            if hwnd is None:
                hwnd = self.user32.GetForegroundWindow()
            
            if not hwnd:
                return {'success': False, 'message': '无法获取目标窗口'}
            
            self.user32.ShowWindow(hwnd, state.value)
            
            return {
                'success': True,
                'message': f'窗口{action}操作完成',
                'action': f'{action}_window',
                'hwnd': hwnd
            }
        except Exception as e:
            return {'success': False, 'message': f'窗口{action}操作失败: {str(e)}'}
    
    # =================== 系统控制 ===================
    def lock_screen(self) -> dict:
        """锁定屏幕"""
        try:
            self.user32.LockWorkStation()
            return {'success': True, 'message': '屏幕已锁定', 'action': 'lock_screen'}
        except Exception as e:
            return {'success': False, 'message': f'锁定屏幕失败: {str(e)}'}
    
    def shutdown_system(self, force: bool = False) -> dict:
        """关机"""
        try:
            flags = '/s /t 0'
            if force:
                flags += ' /f'
            
            subprocess.run(['shutdown', *flags.split()], check=True)
            return {'success': True, 'message': '系统关机命令已发送', 'action': 'shutdown'}
        except Exception as e:
            return {'success': False, 'message': f'关机失败: {str(e)}'}
    
    def restart_system(self, force: bool = False) -> dict:
        """重启"""
        try:
            flags = '/r /t 0'
            if force:
                flags += ' /f'
            
            subprocess.run(['shutdown', *flags.split()], check=True)
            return {'success': True, 'message': '系统重启命令已发送', 'action': 'restart'}
        except Exception as e:
            return {'success': False, 'message': f'重启失败: {str(e)}'}
    
    def sleep_system(self) -> dict:
        """休眠系统"""
        try:
            subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'], check=True)
            return {'success': True, 'message': '系统休眠命令已发送', 'action': 'sleep'}
        except Exception as e:
            return {'success': False, 'message': f'休眠失败: {str(e)}'}
    
    # =================== 快捷键发送 ===================
    def send_key_combination(self, keys: List[int], delay: float = 0.05) -> dict:
        """发送组合键"""
        try:
            # 按下所有键
            for key in keys:
                self.user32.keybd_event(key, 0, 0, 0)
                time.sleep(delay)
            
            # 释放所有键（逆序）
            for key in reversed(keys):
                self.user32.keybd_event(key, 0, 2, 0)
                time.sleep(delay)
            
            return {
                'success': True,
                'message': f'组合键已发送: {[hex(k) for k in keys]}',
                'action': 'send_key_combination',
                'keys': keys
            }
        except Exception as e:
            return {'success': False, 'message': f'发送组合键失败: {str(e)}'}
    
    def send_alt_tab(self) -> dict:
        """发送 Alt+Tab"""
        return self.send_key_combination([0x12, 0x09])  # Alt + Tab
    
    def send_ctrl_c(self) -> dict:
        """发送 Ctrl+C (复制)"""
        return self.send_key_combination([0x11, 0x43])  # Ctrl + C
    
    def send_ctrl_v(self) -> dict:
        """发送 Ctrl+V (粘贴)"""
        return self.send_key_combination([0x11, 0x56])  # Ctrl + V
    
    def send_win_d(self) -> dict:
        """发送 Win+D (显示桌面)"""
        return self.send_key_combination([0x5B, 0x44])  # Win + D
    
    # =================== 系统信息 ===================
    def get_system_info(self) -> dict:
        """获取系统信息"""
        try:
            import platform
            import psutil
            
            return {
                'success': True,
                'system_info': {
                    'platform': platform.platform(),
                    'processor': platform.processor(),
                    'architecture': platform.architecture(),
                    'memory': {
                        'total': psutil.virtual_memory().total,
                        'available': psutil.virtual_memory().available,
                        'percent': psutil.virtual_memory().percent
                    },
                    'disk': {
                        'total': psutil.disk_usage('C:').total,
                        'free': psutil.disk_usage('C:').free,
                        'percent': psutil.disk_usage('C:').percent
                    },
                    'cpu_percent': psutil.cpu_percent(interval=1)
                }
            }
        except ImportError:
            return {'success': False, 'message': '需要安装 psutil: pip install psutil'}
        except Exception as e:
            return {'success': False, 'message': f'获取系统信息失败: {str(e)}'}

# 创建全局实例
system_controller = WindowsSystemController()
