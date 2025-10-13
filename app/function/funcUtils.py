# coding:utf-8
"""
工具函数文件
"""
import threading
import time
import requests
import json
import re
import os
import stat
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import Qt, Signal, QObject, QThread
from qfluentwidgets import InfoBar, InfoBarPosition, SettingCard, ComboBox

# 添加项目根目录到Python路径
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.function.variableConfig import LOG_CONFIG, INSTALL_CONFIG
from app.function.logManager import logMessage, logWarning, logError, getLogger


class SimpleComboBoxSettingCard(SettingCard):
    """简化的组合框设置卡片"""
    
    def __init__(self, icon, title, content=None, texts=None, configItem=None, parent=None):
        super().__init__(icon, title, content, parent)
        self.comboBox = ComboBox(self)
        self.configItem = configItem
        
        if texts:
            self.comboBox.addItems(texts)
        
        # 如果提供了配置项，设置当前值
        if configItem:
            self.setValue(configItem.value)
        
        self.hBoxLayout.addWidget(self.comboBox, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
    
    def setValue(self, value):
        """设置组合框的值"""
        if self.configItem:
            # 根据配置项类型设置值
            if hasattr(self.configItem, 'options'):
                # 选项配置项
                for i, option in enumerate(self.configItem.options):
                    if option == value:
                        self.comboBox.setCurrentIndex(i)
                        break
            else:
                # 普通配置项
                for i in range(self.comboBox.count()):
                    if self.comboBox.itemText(i) == str(value):
                        self.comboBox.setCurrentIndex(i)
                        break
    
    def value(self):
        """获取组合框的值"""
        return self.comboBox.currentText()
    
    def connectValueChanged(self, slot):
        """连接值改变信号"""
        self.comboBox.currentTextChanged.connect(slot)


class ServerLoader(QObject):
    """服务器加载器"""
    serversLoaded = Signal(dict)  # 服务器加载完成信号
    loadFailed = Signal(str)      # 加载失败信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.servers_data = None
        self.load_event = threading.Event()
        
    def loadServers(self):
        """从多个源加载服务器列表"""
        logMessage("开始从多个源加载服务器列表...")
        
        # 创建两个线程分别从不同源加载
        github_thread = threading.Thread(target=self._loadFromSource, args=("GitHub", "https://raw.githubusercontent.com/YvonneOfficial/Temp-Resources/main/servers.dat"))
        mirror_thread = threading.Thread(target=self._loadFromSource, args=("镜像源", "https://gh-proxy.com/https://raw.githubusercontent.com/YvonneOfficial/Temp-Resources/main/servers.dat"))
        
        # 启动线程
        github_thread.start()
        mirror_thread.start()
        
        # 等待任一线程完成
        self.load_event.wait()
        
        # 等待两个线程完成（为了日志完整性）
        github_thread.join(timeout=1)
        mirror_thread.join(timeout=1)
        
        # 如果没有成功加载数据，则发出失败信号
        if self.servers_data is None:
            self.loadFailed.emit("所有源都加载失败")
    
    def _loadFromSource(self, source_name, url):
        """从指定源加载数据"""
        try:
            logMessage(f"正在从{source_name}加载: {url}")
            start_time = time.time()
            
            # 发送GET请求
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # 检查请求是否成功
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # 检查是否已经有其他线程完成加载
            if self.load_event.is_set():
                logMessage(f"从{source_name}加载完成，耗时: {elapsed_time:.2f}秒，但数据已被采用，此数据被忽略")
                return
            
            logMessage(f"从{source_name}加载完成，耗时: {elapsed_time:.2f}秒")
            
            # 解析自定义格式数据
            servers_data = self.parseServerConfig(response.text)
            
            # 转换数据格式以匹配现有代码
            server_config = {}
            for i, (name, filename) in enumerate(servers_data.items()):
                server_id = f"server{i+1}"
                server_config[server_id] = {
                    "name": name,
                    "filename": filename,
                    "enabled": False  # 默认不启用任何服务器
                }
            
            # 检查是否已经有其他线程完成加载
            if not self.load_event.is_set():
                self.servers_data = server_config
                self.load_event.set()  # 通知其他线程已经有结果了
                logMessage(f"使用{source_name}的数据")
                # 发出加载完成信号
                self.serversLoaded.emit(server_config)
            else:
                logMessage(f"{source_name}返回的数据被忽略（已有更快的源）")
                    
        except requests.exceptions.RequestException as e:
            error_msg = f"从{source_name}加载失败: {str(e)}"
            logError(error_msg)
            # 检查是否所有线程都失败了
            if not self.load_event.is_set():
                # 可以在这里添加重试逻辑或其他错误处理
                pass
        except Exception as e:
            error_msg = f"从{source_name}加载时发生未知错误: {str(e)}"
            logError(error_msg)
    
    def parseServerConfig(self, content):
        """解析服务器配置文件"""
        servers = {}
        # 使用正则表达式匹配 "名称" = "文件名" 格式
        pattern = r'"([^"]+)"\s*=\s*"([^"]+)"'
        matches = re.findall(pattern, content)
        
        for name, filename in matches:
            servers[name] = filename
            
        return servers


class ServerConfigLoader(QThread):
    """服务器配置加载器"""
    configLoaded = Signal(list)  # 配置加载完成信号
    loadFailed = Signal(str)     # 加载失败信号
    
    def __init__(self, servers, parent=None):
        super().__init__(parent)
        self.servers = servers
        self.config_data = []
        
    def run(self):
        """在单独的线程中运行"""
        try:
            self.config_data = []
            
            # 为每个服务器加载配置
            for server in self.servers:
                server_name = server['name']
                filename = server['filename']
                
                # 从GitHub和镜像源同时加载
                github_url = f"https://raw.githubusercontent.com/YvonneOfficial/Temp-Resources/main/Servers/{filename}"
                mirror_url = f"https://gh-proxy.com/https://raw.githubusercontent.com/YvonneOfficial/Temp-Resources/main/Servers/{filename}"
                
                # 使用线程事件来实现双线程加载
                server_load_event = threading.Event()
                server_config = [None]  # 使用列表来允许内部函数修改
                
                def load_from_github():
                    try:
                        logMessage(f"正在从GitHub加载服务器配置: {server_name} ({filename})")
                        start_time = time.time()
                        response = requests.get(github_url, timeout=10)
                        response.raise_for_status()
                        server_data = response.json()
                        end_time = time.time()
                        
                        if not server_load_event.is_set():
                            server_config[0] = server_data
                            server_load_event.set()
                            logMessage(f"从GitHub加载服务器配置完成: {server_name}，耗时: {end_time - start_time:.2f}秒")
                    except Exception as e:
                        logError(f"从GitHub加载服务器配置 {server_name} 失败: {str(e)}")
                        # 检查是否两个线程都失败了
                        if not server_load_event.is_set():
                            # 如果镜像线程也完成了，就发出失败信号
                            server_load_event.set()
                        
                def load_from_mirror():
                    try:
                        logMessage(f"正在从镜像源加载服务器配置: {server_name} ({filename})")
                        start_time = time.time()
                        response = requests.get(mirror_url, timeout=10)
                        response.raise_for_status()
                        server_data = response.json()
                        end_time = time.time()
                        
                        if not server_load_event.is_set():
                            server_config[0] = server_data
                            server_load_event.set()
                            logMessage(f"从镜像源加载服务器配置完成: {server_name}，耗时: {end_time - start_time:.2f}秒")
                    except Exception as e:
                        logError(f"从镜像源加载服务器配置 {server_name} 失败: {str(e)}")
                        # 检查是否两个线程都失败了
                        if not server_load_event.is_set():
                            # 如果GitHub线程也完成了，就发出失败信号
                            server_load_event.set()
                
                # 创建并启动两个线程
                github_thread = threading.Thread(target=load_from_github)
                mirror_thread = threading.Thread(target=load_from_mirror)
                
                github_thread.start()
                mirror_thread.start()
                
                # 等待任一线程完成
                server_load_event.wait()  # 立即等待，不设置超时
                
                # 等待两个线程结束
                github_thread.join(timeout=1)
                mirror_thread.join(timeout=1)
                
                # 如果成功加载了配置，添加到结果中
                if server_config[0] is not None:
                    server_data = server_config[0]
                    if isinstance(server_data, list):
                        self.config_data.extend(server_data)
                    else:
                        self.config_data.append(server_data)
                else:
                    logError(f"无法从任何源加载服务器配置: {server_name}")
                    # 如果这是最后一个服务器且没有加载任何配置，则发出失败信号
                    if not self.config_data:
                        self.loadFailed.emit(f"无法从任何源加载服务器配置: {server_name}")
                        return
            
            # 发出加载完成信号
            if self.config_data:
                self.configLoaded.emit(self.config_data)
            else:
                self.loadFailed.emit("未能加载任何服务器配置")
            
        except Exception as e:
            error_msg = f"加载服务器配置时发生错误: {str(e)}"
            logError(error_msg)
            self.loadFailed.emit(error_msg)
            # 确保事件被设置，防止无限等待
            server_load_event.set()


def showInfoBar(parent, title, content, position=InfoBarPosition.TOP):
    """显示信息栏"""
    InfoBar.info(title, content, duration=3000, parent=parent, position=position)


def toggleServerState(serverConfig, serverId, state):
    """切换服务器状态"""
    serverConfig[serverId]['enabled'] = (state == Qt.CheckState.Checked.value)
    return serverConfig


def getEnabledServers(serverConfig):
    """获取启用的服务器列表"""
    return [config for config in serverConfig.values() if config['enabled']]


def installPrivateServer(serverConfig, logCallback, messageCallback):
    """安装私服"""
    enabledServers = getEnabledServers(serverConfig)
    
    if not enabledServers:
        messageCallback('错误', '请至少选择一个服务器！', InfoBarPosition.TOP)
        return False
        
    server_names = [s['name'] for s in enabledServers]
    logCallback(f"开始安装私服，选择的服务器: {', '.join(server_names)}")
    
    # 创建安装线程
    def installThread():
        try:
            # 获取启用的服务器配置
            success, server_count, error_msg = fetchAndInstallServers(enabledServers, logCallback)
            
            if success:
                logCallback("私服安装完成！")
                # 检查是否有重复项
                if error_msg and error_msg.isdigit():
                    duplicate_count = int(error_msg)
                    actual_installed = server_count - duplicate_count
                    if duplicate_count > 0:
                        # 通知调用者安装成功，包含实际安装的服务器数量和重复项数量
                        messageCallback('成功', f'私服安装成功！成功安装 {actual_installed} 个服务器配置，{duplicate_count} 个配置已存在。', InfoBarPosition.TOP)
                    else:
                        # 通知调用者安装成功，包含服务器数量
                        messageCallback('成功', f'私服安装成功！成功安装 {actual_installed} 个服务器配置。', InfoBarPosition.TOP)
                else:
                    # 通知调用者安装成功，包含服务器数量
                    messageCallback('成功', f'私服安装成功！成功安装 {server_count} 个服务器配置。', InfoBarPosition.TOP)
            else:
                logCallback(f"私服安装失败！错误: {error_msg}")
                # 检查是否所有服务器都是重复项
                if error_msg == "检测到所有服务器配置均与现有配置重复，已取消本次安装":
                    # 通知调用者安装取消，使用警告颜色
                    messageCallback('警告', error_msg, InfoBarPosition.TOP)
                else:
                    # 通知调用者安装失败，显示详细错误信息
                    messageCallback('错误', f'安装失败: {error_msg}', InfoBarPosition.TOP)
        except Exception as e:
            error_msg = str(e)
            logError(f"安装过程中发生错误: {error_msg}")
            logCallback(f"安装过程中发生错误: {error_msg}")
            messageCallback('错误', f'安装失败: {error_msg}', InfoBarPosition.TOP)
    
    thread = threading.Thread(target=installThread)
    thread.daemon = True  # 设置为守护线程，确保主程序退出时线程也会退出
    thread.start()
    return True


def fetchAndInstallServers(servers, logCallback):
    """获取并安装服务器配置"""
    try:
        # 1. 使用专用线程获取服务器配置
        config_loader = ServerConfigLoader(servers)
        
        # 创建事件等待配置加载完成
        config_event = threading.Event()
        loaded_configs = []
        load_error = None
        
        def onConfigLoaded(configs):
            loaded_configs.extend(configs)
            config_event.set()
            
        def onLoadFailed(error_msg):
            nonlocal load_error
            load_error = error_msg
            config_event.set()
        
        config_loader.configLoaded.connect(onConfigLoaded, Qt.DirectConnection)
        config_loader.loadFailed.connect(onLoadFailed, Qt.DirectConnection)
        
        # 启动配置加载
        config_loader.start()
        config_event.wait()  # 立即等待加载完成，不设置超时
        
        # 等待线程完成
        config_loader.wait()
        
        if load_error:
            logError(f"服务器配置加载失败: {load_error}")
            return False, 0, f"服务器配置加载失败: {load_error}"
        
        if not loaded_configs:
            error_msg = "未能加载任何服务器配置"
            logError(error_msg)
            return False, 0, error_msg
        
        server_regions = loaded_configs
        server_count = len(server_regions)
        logCallback(f"成功加载 {server_count} 个服务器配置")
        
        # 2. 读取现有的regionInfo.json文件
        # 使用正确的路径：%APPDATA%\..\LocalLow\Innersloth\Among Us\regionInfo.json
        appdata_path = Path(os.getenv('APPDATA'))
        region_file_path = appdata_path.parent / "LocalLow" / "Innersloth" / "Among Us" / "regionInfo.json"
        
        logCallback(f"正在读取regionInfo文件: {region_file_path}")
        
        # 确保目录存在
        region_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 3. 处理文件只读属性
        if region_file_path.exists():
            # 获取当前文件属性
            current_permissions = region_file_path.stat().st_mode
            # 检查是否为只读
            if not (current_permissions & stat.S_IWRITE):
                # 移除只读属性
                region_file_path.chmod(current_permissions | stat.S_IWRITE)
                logCallback("已移除regionInfo文件的只读属性")
        
        # 如果文件不存在，创建一个基础文件
        if not region_file_path.exists():
            base_region_info = {
                "CurrentRegionIdx": 0,
                "Regions": []
            }
            with open(region_file_path, 'w', encoding='utf-8') as f:
                json.dump(base_region_info, f, ensure_ascii=False, indent=2)
            logCallback("已创建基础regionInfo文件")
        
        # 读取现有文件
        try:
            with open(region_file_path, 'r', encoding='utf-8') as f:
                region_info = json.load(f)
        except Exception as e:
            error_msg = f"读取regionInfo文件失败: {str(e)}"
            logError(error_msg)
            return False, 0, error_msg
        
        # 4. 添加新的服务器配置
        if "Regions" not in region_info:
            region_info["Regions"] = []
        
        # 检查重复的服务器配置
        existing_regions = region_info["Regions"]
        unique_server_regions = []
        duplicate_count = 0
        
        for new_region in server_regions:
            # 检查是否与现有配置重复（基于PingServer和Ip）
            is_duplicate = False
            new_ping_server = new_region.get("PingServer", "")
            new_ip = new_region.get("Ip", "")
            
            for existing_region in existing_regions:
                existing_ping_server = existing_region.get("PingServer", "")
                existing_ip = existing_region.get("Ip", "")
                
                if new_ping_server == existing_ping_server and new_ip == existing_ip:
                    is_duplicate = True
                    duplicate_count += 1
                    logCallback(f"跳过重复的服务器配置: {new_region.get('Name', 'Unknown')}")
                    break
            
            # 如果不是重复项，则添加到待安装列表
            if not is_duplicate:
                unique_server_regions.append(new_region)
        
        # 如果所有配置都重复，则提示安装取消
        if duplicate_count > 0 and len(unique_server_regions) == 0:
            logCallback("所有服务器配置都是重复项，跳过安装")
            # 恢复只读属性
            region_file_path.chmod(stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
            logCallback("已恢复regionInfo文件的只读属性")
            return False, 0, "检测到所有服务器配置均与现有配置重复，已取消本次安装"
        
        # 添加新的服务器区域
        original_count = len(region_info["Regions"])
        region_info["Regions"].extend(unique_server_regions)
        new_count = len(region_info["Regions"])
        added_count = new_count - original_count
        
        logCallback(f"已添加 {added_count} 个新服务器区域")
        
        # 5. 保存更新后的文件
        with open(region_file_path, 'w', encoding='utf-8') as f:
            json.dump(region_info, f, ensure_ascii=False, indent=2)
        
        # 6. 恢复只读属性
        region_file_path.chmod(stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
        logCallback("已恢复regionInfo文件的只读属性")
        
        logCallback(f"已保存更新的regionInfo文件到: {region_file_path}")
        return True, server_count, f"{duplicate_count}"  # 成功，返回服务器数量和重复项数量
        
    except Exception as e:
        error_msg = str(e)
        logError(f"安装服务器时发生错误: {error_msg}")
        return False, 0, "安装失败"  # 失败，返回简单错误信息