from flask import Flask, jsonify, request
from flask_cors import CORS
from windows_controller import system_controller
import json

app = Flask(__name__)
CORS(app)

# 通用的请求数据获取函数
def get_request_data():
    """安全地获取请求数据，避免JSON解析错误"""
    try:
        # 对于GET请求，优先使用查询参数
        if request.method == 'GET':
            return dict(request.args)
        print(request.data)
        # 对于POST请求
        if request.method == 'POST':
            # 检查是否有JSON数据且Content-Type正确
            if request.is_json and request.content_type == 'application/json':
                return request.get_json() or {}
            # 检查表单数据
            elif request.data:
                try:
                    json_str = request.data.decode('utf-8')
                    data = json.loads(json_str)
                    return data
                except Exception as e:
                    print(f"解析body json出错: {e}")
                    return {}
            # 如果没有数据，返回空字典
            else:
                return {}
        
        # 默认返回空字典
        return {}
        
    except Exception as e:
        print(f"获取请求数据时出错: {e}")
        return {}

# =================== 音量控制 API ===================
@app.route('/api/volume/<action>', methods=['GET', 'POST'])
def volume_control(action: str):
    """音量控制"""
    try:
        print(f"收到音量控制请求: {action}, 方法: {request.method}")
        
        data = get_request_data()
        print(f"请求数据: {data}")
        
        steps = 1
        try:
            steps = int(data.get('steps', 1))
        except (ValueError, TypeError):
            steps = 1
        
        actions = {
            'up': lambda: system_controller.volume_up(steps),
            'down': lambda: system_controller.volume_down(steps),
            'mute': lambda: system_controller.volume_mute()
        }
        
        if action not in actions:
            return jsonify({
                'success': False, 
                'message': f'不支持的操作: {action}',
                'available_actions': list(actions.keys())
            }), 400
        
        print(f"执行音量操作: {action}")
        result = actions[action]()
        print(f"操作结果: {result}")
        
        return jsonify(result), 200 if result.get('success', False) else 400
        
    except Exception as e:
        print(f"音量控制错误: {e}")
        return jsonify({
            'success': False, 
            'message': f'服务器错误: {str(e)}'
        }), 500

# =================== 媒体控制 API ===================
@app.route('/api/media/<action>', methods=['GET', 'POST'])
def media_control(action: str):
    """媒体控制"""
    try:
        print(f"收到媒体控制请求: {action}, 方法: {request.method}")
        
        actions = {
            'play': lambda: system_controller.media_play_pause(),
            'pause': lambda: system_controller.media_play_pause(),
            'stop': lambda: system_controller.media_stop(),
            'next': lambda: system_controller.media_next(),
            'previous': lambda: system_controller.media_previous()
        }
        
        if action not in actions:
            return jsonify({
                'success': False, 
                'message': f'不支持的操作: {action}',
                'available_actions': list(actions.keys())
            }), 400
        
        print(f"执行媒体操作: {action}")
        result = actions[action]()
        print(f"操作结果: {result}")
        
        return jsonify(result), 200 if result.get('success', False) else 400
        
    except Exception as e:
        print(f"媒体控制错误: {e}")
        return jsonify({
            'success': False, 
            'message': f'服务器错误: {str(e)}'
        }), 500

# =================== 屏幕亮度 API ===================
@app.route('/api/brightness/<action>', methods=['GET', 'POST'])
def brightness_control(action: str):
    """屏幕亮度控制"""
    try:
        print(f"收到亮度控制请求: {action}, 方法: {request.method}")
        
        data = get_request_data()
        steps = 1
        try:
            steps = int(data.get('steps', 1))
        except (ValueError, TypeError):
            steps = 1
        
        actions = {
            'up': lambda: system_controller.brightness_up(steps),
            'down': lambda: system_controller.brightness_down(steps)
        }
        
        if action not in actions:
            return jsonify({
                'success': False, 
                'message': f'不支持的操作: {action}',
                'available_actions': list(actions.keys())
            }), 400
        
        print(f"执行亮度操作: {action}")
        result = actions[action]()
        print(f"操作结果: {result}")
        
        return jsonify(result), 200 if result.get('success', False) else 400
        
    except Exception as e:
        print(f"亮度控制错误: {e}")
        return jsonify({
            'success': False, 
            'message': f'服务器错误: {str(e)}'
        }), 500

# =================== 应用程序控制 API ===================
@app.route('/api/app/launch', methods=['GET', 'POST'])
def launch_app():
    """启动应用程序"""
    try:
        print(f"收到应用启动请求, 方法: {request.method}")
        
        data = get_request_data()
        print(f"请求数据: {data}")
        
        if not data or 'path' not in data:
            return jsonify({
                'success': False, 
                'message': '请提供应用程序路径',
                'example': {'path': 'C:\\Windows\\System32\\notepad.exe'}
            }), 400
        
        result = system_controller.launch_application(
            data['path'], 
            data.get('args', ''), 
            data.get('working_dir', '')
        )
        return jsonify(result), 200 if result.get('success', False) else 400
        
    except Exception as e:
        print(f"应用启动错误: {e}")
        return jsonify({
            'success': False, 
            'message': f'服务器错误: {str(e)}'
        }), 500

@app.route('/api/app/kill', methods=['GET', 'POST'])
def kill_app():
    """终止应用程序"""
    try:
        print(f"收到应用终止请求, 方法: {request.method}")
        
        data = get_request_data()
        
        if not data or 'name' not in data:
            return jsonify({
                'success': False, 
                'message': '请提供进程名称',
                'example': {'name': 'notepad.exe'}
            }), 400
        
        result = system_controller.kill_process(data['name'])
        return jsonify(result), 200 if result.get('success', False) else 400
        
    except Exception as e:
        print(f"应用终止错误: {e}")
        return jsonify({
            'success': False, 
            'message': f'服务器错误: {str(e)}'
        }), 500

@app.route('/api/app/processes', methods=['GET'])
def get_processes():
    """获取进程列表"""
    try:
        print("收到获取进程列表请求")
        result = system_controller.get_running_processes()
        return jsonify(result), 200 if result.get('success', False) else 400
    except Exception as e:
        print(f"获取进程列表错误: {e}")
        return jsonify({
            'success': False, 
            'message': f'服务器错误: {str(e)}'
        }), 500

# =================== 窗口控制 API ===================
@app.route('/api/window/<action>', methods=['GET', 'POST'])
def window_control(action: str):
    """窗口控制"""
    try:
        print(f"收到窗口控制请求: {action}, 方法: {request.method}")
        
        data = get_request_data()
        hwnd = data.get('hwnd')
        if hwnd:
            try:
                hwnd = int(hwnd)
            except (ValueError, TypeError):
                hwnd = None
        
        actions = {
            'minimize': lambda: system_controller.minimize_window(hwnd),
            'maximize': lambda: system_controller.maximize_window(hwnd),
            'restore': lambda: system_controller.restore_window(hwnd),
            'close': lambda: system_controller.close_window(hwnd),
            'info': lambda: system_controller.get_active_window()
        }
        
        if action not in actions:
            return jsonify({
                'success': False, 
                'message': f'不支持的操作: {action}',
                'available_actions': list(actions.keys())
            }), 400
        
        print(f"执行窗口操作: {action}")
        result = actions[action]()
        print(f"操作结果: {result}")
        
        return jsonify(result), 200 if result.get('success', False) else 400
        
    except Exception as e:
        print(f"窗口控制错误: {e}")
        return jsonify({
            'success': False, 
            'message': f'服务器错误: {str(e)}'
        }), 500

# =================== 系统控制 API ===================
@app.route('/api/system/<action>', methods=['GET', 'POST'])
def system_control(action: str):
    """系统控制"""
    try:
        print(f"收到系统控制请求: {action}, 方法: {request.method}")
        
        data = get_request_data()
        force = str(data.get('force', '')).lower() in ['true', '1', 'yes']
        
        actions = {
            'lock': lambda: system_controller.lock_screen(),
            'shutdown': lambda: system_controller.shutdown_system(force),
            'restart': lambda: system_controller.restart_system(force),
            'sleep': lambda: system_controller.sleep_system(),
            'info': lambda: system_controller.get_system_info()
        }
        
        if action not in actions:
            return jsonify({
                'success': False, 
                'message': f'不支持的操作: {action}',
                'available_actions': list(actions.keys())
            }), 400
        
        print(f"执行系统操作: {action}")
        result = actions[action]()
        print(f"操作结果: {result}")
        
        return jsonify(result), 200 if result.get('success', False) else 400
        
    except Exception as e:
        print(f"系统控制错误: {e}")
        return jsonify({
            'success': False, 
            'message': f'服务器错误: {str(e)}'
        }), 500

# =================== 快捷键 API ===================
@app.route('/api/hotkey/<action>', methods=['GET', 'POST'])
def hotkey_control(action: str):
    """快捷键控制"""
    try:
        print(f"收到快捷键请求: {action}, 方法: {request.method}")
        
        actions = {
            'alt_tab': lambda: system_controller.send_alt_tab(),
            'ctrl_c': lambda: system_controller.send_ctrl_c(),
            'ctrl_v': lambda: system_controller.send_ctrl_v(),
            'win_d': lambda: system_controller.send_win_d()
        }
        
        if action not in actions:
            return jsonify({
                'success': False, 
                'message': f'不支持的操作: {action}',
                'available_actions': list(actions.keys())
            }), 400
        
        print(f"执行快捷键: {action}")
        result = actions[action]()
        print(f"操作结果: {result}")
        
        return jsonify(result), 200 if result.get('success', False) else 400
        
    except Exception as e:
        print(f"快捷键控制错误: {e}")
        return jsonify({
            'success': False, 
            'message': f'服务器错误: {str(e)}'
        }), 500

@app.route('/api/hotkey/custom', methods=['GET', 'POST'])
def custom_hotkey():
    """自定义组合键"""
    try:
        print(f"收到自定义快捷键请求, 方法: {request.method}")
        
        data = get_request_data()
        
        if not data or 'keys' not in data:
            return jsonify({
                'success': False, 
                'message': '请提供按键列表',
                'example': {'keys': '[17,67]'}  # Ctrl+C
            }), 400
        
        keys = data['keys']
        if isinstance(keys, str):
            try:
                import json
                keys = json.loads(keys)
            except:
                return jsonify({
                    'success': False, 
                    'message': 'keys 格式错误，应为JSON数组'
                }), 400
        
        if not isinstance(keys, list):
            return jsonify({
                'success': False, 
                'message': 'keys 必须是数组'
            }), 400
        
        result = system_controller.send_key_combination(keys)
        return jsonify(result), 200 if result.get('success', False) else 400
        
    except Exception as e:
        print(f"自定义快捷键错误: {e}")
        return jsonify({
            'success': False, 
            'message': f'服务器错误: {str(e)}'
        }), 500

# =================== 测试端点 ===================
@app.route('/api/test', methods=['GET', 'POST'])
def test_endpoint():
    """测试端点"""
    try:
        import time
        data = get_request_data()
        
        print(f"收到测试请求, 方法: {request.method}, 数据: {data}")
        
        return jsonify({
            'success': True,
            'message': 'API 服务正常运行',
            'method': request.method,
            'data_received': data,
            'timestamp': time.time(),
            'server_status': 'online',
            'content_type': request.content_type,
            'headers': dict(request.headers)
        })
        
    except Exception as e:
        print(f"测试端点错误: {e}")
        return jsonify({
            'success': False, 
            'message': f'服务器错误: {str(e)}'
        }), 500

# =================== API 信息 ===================
@app.route('/api/info', methods=['GET'])
def api_info():
    """获取 API 信息"""
    return jsonify({
        'success': True,
        'message': 'Windows 系统控制 API',
        'server_info': {
            'version': '1.0.1',
            'supported_methods': ['GET', 'POST'],
            'content_types': ['application/json', 'application/x-www-form-urlencoded', 'query_params'],
            'note': 'GET请求使用查询参数，POST请求支持JSON和表单数据'
        },
        'categories': {
            'volume': {
                'endpoints': ['/api/volume/up', '/api/volume/down', '/api/volume/mute'],
                'description': '音量控制',
                'parameters': {'steps': 'int (可选, 默认1)'}
            },
            'media': {
                'endpoints': ['/api/media/play', '/api/media/stop', '/api/media/next', '/api/media/previous'],
                'description': '媒体播放控制'
            },
            'brightness': {
                'endpoints': ['/api/brightness/up', '/api/brightness/down'],
                'description': '屏幕亮度控制',
                'parameters': {'steps': 'int (可选, 默认1)'}
            },
            'application': {
                'endpoints': ['/api/app/launch', '/api/app/kill', '/api/app/processes'],
                'description': '应用程序控制'
            },
            'window': {
                'endpoints': ['/api/window/minimize', '/api/window/maximize', '/api/window/restore', '/api/window/close', '/api/window/info'],
                'description': '窗口控制'
            },
            'system': {
                'endpoints': ['/api/system/lock', '/api/system/shutdown', '/api/system/restart', '/api/system/sleep', '/api/system/info'],
                'description': '系统控制'
            },
            'hotkey': {
                'endpoints': ['/api/hotkey/alt_tab', '/api/hotkey/ctrl_c', '/api/hotkey/ctrl_v', '/api/hotkey/win_d', '/api/hotkey/custom'],
                'description': '快捷键控制'
            }
        },
        'examples': {
            'simple_get': 'GET /api/volume/up',
            'get_with_params': 'GET /api/volume/up?steps=3',
            'post_json': 'POST /api/volume/up {"steps": 3}',
            'post_form': 'POST /api/volume/up (form: steps=3)'
        }
    })

# =================== 根路径 ===================
@app.route('/')
def index():
    """根路径"""
    return jsonify({
        'message': 'Windows 系统控制 API 服务器',
        'api_info': '/api/info',
        'test_endpoint': '/api/test',
        'status': 'running'
    })

if __name__ == '__main__':
    print("🖥️  Windows 系统控制服务器启动中...")
    print("📡 API 信息: http://localhost:8090/api/info")
    print("🧪 测试端点: http://localhost:8090/api/test")
    print("🔊 音量控制: http://localhost:8090/api/volume/up")
    print("💡 支持 GET 和 POST 请求")
    print("🔍 调试模式已开启，将显示详细日志")
    app.run(host='0.0.0.0', port=8090, debug=True)
