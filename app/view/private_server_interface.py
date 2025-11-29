# coding: utf-8
import json
import os
import stat
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget
from qfluentwidgets import ScrollArea, HeaderCardWidget, CheckBox, BodyLabel, setFont, PrimaryPushButton, InfoBar, InfoBarPosition
from ..common.style_sheet import StyleSheet


class PrivateServerCard(HeaderCardWidget):
    """ Private server card with checkboxes """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr('Servers'))
        
        # 存储服务器选项的字典
        self.server_options = {}
        
        # 创建垂直布局
        self.vBoxLayout = QVBoxLayout()
        
        # 加载服务器选项
        self.loadServerOptions()
        
        # 使用HeaderCardWidget的viewLayout添加内容
        self.viewLayout.addLayout(self.vBoxLayout)
    
    def loadServerOptions(self):
        """ 加载servers.json中的服务器选项 """
        try:
            # 获取项目根目录下的servers.json文件路径
            servers_json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'servers.json')
            
            # 读取servers.json文件
            with open(servers_json_path, 'r', encoding='utf-8') as f:
                servers_data = json.load(f)
            
            # 为每个服务器创建复选框
            for server_name in servers_data:
                checkbox = CheckBox(server_name, self)
                self.server_options[server_name] = checkbox
                self.vBoxLayout.addWidget(checkbox)
                
        except Exception as e:
            print(f"加载服务器选项时出错: {e}")


class PrivateServerInterface(ScrollArea):
    """ Private Server interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)
        
        # 添加页面标题
        self.titleLabel = QLabel(self.tr('Private Server Installation'), self)
        
        # 添加HeaderCardWidget组件
        self.headerCard = PrivateServerCard(self)
        
        # 添加"安装私服"按钮
        self.installButton = PrimaryPushButton(self.tr('Install'), self)
        # 连接按钮点击事件
        self.installButton.clicked.connect(self.onInstallButtonClicked)

        self.__initWidget()

    def __initWidget(self):
        self.setObjectName('privateServerInterface')
        self.scrollWidget.setObjectName('scrollWidget')
        StyleSheet.PRIVATE_SERVER_INTERFACE.apply(self)

        # 设置标题样式，与设置界面保持一致
        setFont(self.titleLabel, 23, QFont.Weight.DemiBold)
        self.titleLabel.setObjectName('settingLabel')
        # 移动标题到正确位置（微调水平位置使其更居中）
        self.titleLabel.move(30, 50)
        
        self.setViewportMargins(0, 100, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        
        # 添加HeaderCardWidget到布局（标题不添加到布局中，以保持与设置界面一致的位置）
        self.vBoxLayout.addWidget(self.headerCard)
        # 在卡片下方添加"安装私服"按钮
        self.vBoxLayout.addWidget(self.installButton)
        
        self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setContentsMargins(36, 10, 36, 0)
    
    def onInstallButtonClicked(self):
        """ 处理'安装私服'按钮点击事件 """
        # 获取选中的服务器
        selected_servers = []
        for server_name, checkbox in self.headerCard.server_options.items():
            if checkbox.isChecked():
                selected_servers.append(server_name)
        
        if not selected_servers:
            # 如果没有选择任何服务器，显示提示信息
            InfoBar.warning(
                title=self.tr('提示'),
                content=self.tr('请至少选择一个服务器'),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )
            return
        
        # 安装选中的服务器
        self.installPrivateServers(selected_servers)
    
    def installPrivateServers(self, selected_servers):
        """ 安装选中的私服 """
        try:
            print(f"[DEBUG] 开始安装私服，选中的服务器: {selected_servers}")
            # 读取servers.json文件
            servers_json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'servers.json')
            print(f"[DEBUG] servers.json 路径: {servers_json_path}")
            with open(servers_json_path, 'r', encoding='utf-8') as f:
                servers_data = json.load(f)
            print(f"[DEBUG] 成功加载 servers.json，包含服务器组: {list(servers_data.keys())}")
            
            # 获取Among Us的regionInfo.json文件路径
            import platform
            if platform.system() == "Windows":
                # Windows系统路径
                region_info_path = os.path.expandvars(r'%LOCALAPPDATA%\..\LocalLow\Innersloth\Among Us\regionInfo.json')
            else:
                # 其他系统可能需要不同的路径处理
                region_info_path = os.path.expanduser('~/.steam/steam/steamapps/common/Among Us/regionInfo.json')
            print(f"[DEBUG] regionInfo.json 路径: {region_info_path}")
            
            # 解锁regionInfo.json文件的只读属性（如果文件存在）
            file_existed = os.path.exists(region_info_path)
            if file_existed:
                # 解锁文件（无论是否原来是只读的）
                os.chmod(region_info_path, stat.S_IWRITE)
            print(f"[DEBUG] regionInfo.json 文件是否存在: {file_existed}")
            
            # 检查regionInfo.json文件是否存在，如果不存在则创建一个默认结构
            if os.path.exists(region_info_path):
                # 尝试不同的编码方式读取文件
                encodings = ['utf-8', 'gbk', 'gb2312']
                region_info_data = None
                for encoding in encodings:
                    try:
                        with open(region_info_path, 'r', encoding=encoding) as f:
                            region_info_data = json.load(f)
                            print(f"[DEBUG] 成功使用 {encoding} 编码读取 regionInfo.json 数据")
                            break
                    except (UnicodeDecodeError, json.JSONDecodeError) as e:
                        print(f"[DEBUG] 使用 {encoding} 编码读取失败: {e}")
                        continue
                
                # 如果所有编码都失败，使用默认结构
                if region_info_data is None:
                    region_info_data = {
                        "CurrentRegionIdx": 0,
                        "Regions": []
                    }
                    print("[DEBUG] 所有编码方式都失败，使用默认结构")
            else:
                region_info_data = {
                    "CurrentRegionIdx": 0,
                    "Regions": []
                }
                print("[DEBUG] regionInfo.json 文件不存在，创建默认结构")
            
            # 确保region_info_data是一个字典且包含必要的字段
            if not isinstance(region_info_data, dict):
                region_info_data = {
                    "CurrentRegionIdx": 0,
                    "Regions": []
                }
                print("[DEBUG] regionInfo 数据格式不正确，重置为默认结构")
            
            if "Regions" not in region_info_data:
                region_info_data["Regions"] = []
                print("[DEBUG] regionInfo 中缺少 Regions 字段，已添加")
            
            if "CurrentRegionIdx" not in region_info_data:
                region_info_data["CurrentRegionIdx"] = 0
                print("[DEBUG] regionInfo 中缺少 CurrentRegionIdx 字段，已添加")
            
            # 获取现有的服务器列表
            existing_regions = region_info_data["Regions"]
            print(f"[DEBUG] 当前已存在的服务器列表: {existing_regions}")
            
            # 统计安装数量和重复数量
            installed_count = 0
            duplicate_count = 0
            
            # 为每个选中的服务器生成region条目
            for server_group_name in selected_servers:
                if server_group_name in servers_data:
                    print(f"[DEBUG] 处理服务器组: {server_group_name}")
                    # 遍历该服务器组中的所有服务器
                    for server_info in servers_data[server_group_name]:
                        print(f"[DEBUG] 处理服务器信息: {server_info}")
                        # 创建region条目
                        region_entry = {
                            "$type": "StaticHttpRegionInfo, Assembly-CSharp",
                            "Name": server_info['Name'],
                            "PingServer": server_info['Ip'],
                            "Servers": [
                                {
                                    "Name": "Http-1",
                                    "Ip": server_info['Ip'],
                                    "Port": server_info['Port'],
                                    "UseDtls": False,
                                    "Players": 0,
                                    "ConnectionFailures": 0
                                }
                            ],
                            "TargetServer": None,
                            "TranslateName": 1003
                        }
                        print(f"[DEBUG] 创建的region条目: {region_entry}")
                        
                        # 检查是否已存在相同的服务器
                        is_duplicate = False
                        for existing_entry in existing_regions:
                            if (existing_entry.get('Name') == region_entry['Name'] and 
                                existing_entry.get('PingServer') == region_entry['PingServer']):
                                is_duplicate = True
                                duplicate_count += 1
                                print(f"[DEBUG] 发现重复服务器: {region_entry['Name']}")
                                break
                        
                        # 如果不是重复的服务器，则添加到regionInfo中
                        if not is_duplicate:
                            existing_regions.append(region_entry)
                            installed_count += 1
                            print(f"[DEBUG] 添加新服务器: {region_entry['Name']}")
                        else:
                            print(f"[DEBUG] 跳过重复服务器: {region_entry['Name']}")
            
            # 检查是否所有服务器都是重复的
            if installed_count == 0 and duplicate_count > 0:
                # 所有服务器都重复，显示提示信息
                InfoBar.warning(
                    title=self.tr('安装终止'),
                    content=self.tr('所有服务器均重复'),
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=3000,
                    parent=self
                )
                # 重新设置文件为只读（无论文件原来是否是只读的）
                if os.path.exists(region_info_path):
                    os.chmod(region_info_path, stat.S_IREAD)
                print("[DEBUG] 所有服务器均重复，安装终止")
                return
            
            print(f"[DEBUG] 准备保存文件，新增服务器数: {installed_count}, 重复服务器数: {duplicate_count}")
            
            # 更新regionInfo数据
            region_info_data["Regions"] = existing_regions
            print(f"[DEBUG] 更新后的regionInfo数据: {region_info_data}")
            
            # 保存更新后的regionInfo.json文件
            # 确保目录存在
            os.makedirs(os.path.dirname(region_info_path), exist_ok=True)
            print(f"[DEBUG] 确保目录存在: {os.path.dirname(region_info_path)}")
            
            # 使用UTF-8编码写入文件，确保中文字符正确保存
            with open(region_info_path, 'w', encoding='utf-8') as f:
                json.dump(region_info_data, f, ensure_ascii=False, indent=2)
                print("[DEBUG] 成功写入regionInfo.json文件")
            
            # 重新设置文件为只读（无论文件原来是否是只读的）
            if os.path.exists(region_info_path):
                os.chmod(region_info_path, stat.S_IREAD)
                print("[DEBUG] 设置regionInfo.json为只读")
            
            # 显示成功消息，使用Pangu格式（在中文与英文、数字之间加上空格）
            print(f"[DEBUG] 准备显示成功消息，安装数: {installed_count}, 重复数: {duplicate_count}")
            InfoBar.success(
                title=self.tr('私服安装成功'),
                content=self.tr(f'共安装了 {installed_count} 个服务器，{duplicate_count} 个服务器重复'),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )
            print("[DEBUG] 成功消息已显示")
            
        except Exception as e:
            # 显示错误消息
            InfoBar.error(
                title=self.tr('安装失败'),
                content=self.tr(f'安装过程中发生错误: {str(e)}'),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )