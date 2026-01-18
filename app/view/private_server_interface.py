# coding: utf-8
import json
import logging
import os
import stat
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from qfluentwidgets import ScrollArea, HeaderCardWidget, CheckBox, setFont, PrimaryPushButton, InfoBar, InfoBarPosition
from ..common.style_sheet import StyleSheet

logger = logging.getLogger(__name__)


class PrivateServerCard(HeaderCardWidget):
    """ Private server card with checkboxes """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr('Servers'))

        # 存储服务器选项的字典
        self.server_options = {}

        # 存储从 GitHub 获取的服务器数据
        self.servers_data = None

        # 创建垂直布局
        self.vBoxLayout = QVBoxLayout()

        # 不在初始化时加载服务器选项，等待后台下载完成后加载

        # 使用HeaderCardWidget的viewLayout添加内容
        self.viewLayout.addLayout(self.vBoxLayout)

    def setServersData(self, data):
        """ 设置服务器数据并创建复选框 """
        try:
            self.servers_data = data

            if self.servers_data is None:
                logger.error("失败：服务器数据为空")
                return

            # 为每个服务器创建复选框
            for server_name in self.servers_data:
                checkbox = CheckBox(server_name, self)
                self.server_options[server_name] = checkbox
                self.vBoxLayout.addWidget(checkbox)

            logger.info(f"成功加载服务器选项，共 {len(self.servers_data)} 个服务器组")

        except Exception as e:
            logger.error(f"设置服务器数据时出错: {e}")


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
            logger.debug(f"开始安装私服，选中的服务器: {selected_servers}")
            # 使用已缓存的服务器数据
            servers_data = self.headerCard.servers_data
            if servers_data is None:
                InfoBar.error(
                    title=self.tr('安装失败'),
                    content=self.tr('服务器数据未加载，请检查网络连接'),
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=3000,
                    parent=self
                )
                return

            # 获取Among Us的regionInfo.json文件路径
            import platform
            if platform.system() == "Windows":
                # Windows系统路径
                region_info_path = os.path.expandvars(r'%LOCALAPPDATA%\..\LocalLow\Innersloth\Among Us\regionInfo.json')
            else:
                # 其他系统可能需要不同的路径处理
                region_info_path = os.path.expanduser('~/.steam/steam/steamapps/common/Among Us/regionInfo.json')

            # 解锁regionInfo.json文件的只读属性（如果文件存在）
            file_existed = os.path.exists(region_info_path)
            if file_existed:
                # 解锁文件（无论是否原来是只读的）
                os.chmod(region_info_path, stat.S_IWRITE)

            # 检查regionInfo.json文件是否存在，如果不存在则创建一个默认结构
            if os.path.exists(region_info_path):
                # 尝试不同的编码方式读取文件
                encodings = ['utf-8', 'gbk', 'gb2312']
                region_info_data = None
                for encoding in encodings:
                    try:
                        with open(region_info_path, 'r', encoding=encoding) as f:
                            region_info_data = json.load(f)
                            break
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        continue

                # 如果所有编码都失败，使用默认结构
                if region_info_data is None:
                    region_info_data = {
                        "CurrentRegionIdx": 0,
                        "Regions": []
                    }
                    logger.debug("所有编码方式都失败，使用默认结构")
            else:
                region_info_data = {
                    "CurrentRegionIdx": 0,
                    "Regions": []
                }
                logger.debug("regionInfo.json 文件不存在，创建默认结构")

            # 确保region_info_data是一个字典且包含必要的字段
            if not isinstance(region_info_data, dict):
                region_info_data = {
                    "CurrentRegionIdx": 0,
                    "Regions": []
                }
                logger.debug("regionInfo 数据格式不正确，重置为默认结构")

            if "Regions" not in region_info_data:
                region_info_data["Regions"] = []
                logger.debug("regionInfo 中缺少 Regions 字段，已添加")

            if "CurrentRegionIdx" not in region_info_data:
                region_info_data["CurrentRegionIdx"] = 0
                logger.debug("regionInfo 中缺少 CurrentRegionIdx 字段，已添加")

            # 获取现有的服务器列表
            existing_regions = region_info_data["Regions"]

            # 统计安装数量和重复数量
            installed_count = 0
            duplicate_count = 0

            # 为每个选中的服务器生成region条目
            for server_group_name in selected_servers:
                if server_group_name in servers_data:
                    logger.debug(f"处理服务器组: {server_group_name}")
                    # 遍历该服务器组中的所有服务器
                    for server_info in servers_data[server_group_name]:
                        # 处理 IP，删除 http:// 或 https:// 前缀
                        original_ip = server_info['Ip']
                        ping_server = original_ip
                        if ping_server.startswith('https://'):
                            ping_server = ping_server[8:]
                        elif ping_server.startswith('http://'):
                            ping_server = ping_server[7:]

                        # 创建region条目
                        region_entry = {
                            "$type": "StaticHttpRegionInfo, Assembly-CSharp",
                            "Name": server_info['Name'],
                            "PingServer": ping_server,
                            "Servers": [
                                {
                                    "Name": "Http-1",
                                    "Ip": original_ip,
                                    "Port": server_info['Port'],
                                    "UseDtls": False,
                                    "Players": 0,
                                    "ConnectionFailures": 0
                                }
                            ],
                            "TargetServer": None,
                            "TranslateName": 1003
                        }

                        # 检查是否已存在相同的服务器（通过 Servers[0].Ip 检测）
                        is_duplicate = False
                        for existing_entry in existing_regions:
                            # 连接服务器使用的是 Servers[0].Ip
                            servers = existing_entry.get('Servers', [])
                            if servers and len(servers) > 0:
                                existing_ip = servers[0].get('Ip')
                                if existing_ip == server_info['Ip']:
                                    is_duplicate = True
                                    duplicate_count += 1
                                    logger.debug(f"发现重复服务器: {region_entry['Name']}")
                                    break

                        # 如果不是重复的服务器，则添加到regionInfo中
                        if not is_duplicate:
                            existing_regions.append(region_entry)
                            installed_count += 1
                            logger.debug(f"添加新服务器: {region_entry['Name']}")
                        else:
                            logger.debug(f"跳过重复服务器: {region_entry['Name']}")

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
                logger.debug("所有服务器均重复，安装终止")
                return

            logger.debug(f"准备保存文件，新增服务器数: {installed_count}, 重复服务器数: {duplicate_count}")

            # 更新regionInfo数据
            region_info_data["Regions"] = existing_regions

            # 保存更新后的regionInfo.json文件
            # 确保目录存在
            os.makedirs(os.path.dirname(region_info_path), exist_ok=True)

            # 使用UTF-8编码写入文件，确保中文字符正确保存
            with open(region_info_path, 'w', encoding='utf-8') as f:
                json.dump(region_info_data, f, ensure_ascii=False, indent=2)

            # 重新设置文件为只读（无论文件原来是否是只读的）
            if os.path.exists(region_info_path):
                os.chmod(region_info_path, stat.S_IREAD)

            # 显示成功消息
            InfoBar.success(
                title=self.tr('私服安装成功'),
                content=self.tr(f'共安装了 {installed_count} 个服务器，{duplicate_count} 个服务器重复'),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )

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
